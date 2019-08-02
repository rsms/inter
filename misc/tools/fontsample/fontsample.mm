#import <Foundation/Foundation.h>
#import <CoreGraphics/CoreGraphics.h>
#import <CoreText/CoreText.h>
#import <ImageIO/ImageIO.h>


static const char* prog = "?";

static struct Options {
  NSString* output = nil;
  CGFloat size = 96;
  size_t width = 0;
  size_t height = 0;
  NSString* text = @"Rags78 **A**";
}options{};

static const char usagetemplate[] = ""
"usage: %s [options] <fontfile>\n"
"\n"
"options:\n"
"  -h, -help         Show usage and exit.\n"
"  -z, -size <size>  Font size to render. Defaults to %g.\n"
"  -t, -text <text>  Text line to render. Defaults to \"%s\".\n"
"  -width <pixels>   Make the image <pixels> wide (automatic if not set)\n"
"  -height <pixels>  Make the image <pixels> tall (automatic if not set)\n"
"  -o <file>         Write output to <file> instead of default filename.\n"
"                    Defaults to <fontfile>.pdf. If the provided filename\n"
"                    ends with \".png\" a PNG is written instead of a PDF.\n"
"\n"
"<fontfile>\n"
"  Any font file that macOS can read.\n"
;

void usage() {
  printf(usagetemplate, prog, options.size, options.text.UTF8String);
}


// must call CFRelease on the returned pointer
CTFontRef loadFont(NSString* filename, CGFloat size) {
  CFURLRef url = CFURLCreateWithFileSystemPath(kCFAllocatorDefault, (CFStringRef)filename, kCFURLPOSIXPathStyle, false);

  CGDataProviderRef dataProvider = CGDataProviderCreateWithURL(url);
  if (!dataProvider) {
    fprintf(stderr, "%s: failed to read file %s\n", prog, filename.UTF8String);
    exit(1);
  }

  CGFontRef cgf = CGFontCreateWithDataProvider(dataProvider);
  if (!cgf) {
    fprintf(stderr, "%s: failed to parse font %s\n", prog, filename.UTF8String);
    exit(1);
  }

  CTFontRef ctf = CTFontCreateWithGraphicsFont(cgf, size, nil, nil);
  if (!ctf) {
    fprintf(stderr, "%s: CTFontCreateWithGraphicsFont failed\n", prog);
    exit(1);
  }

  CFRelease(cgf);
  CFRelease(dataProvider);
  CFRelease(url);
  return ctf;
}


CTLineRef createTextLine(CTFontRef font, NSString* text) {
  NSDictionary* attr = @{ (NSString*)kCTFontAttributeName: (__bridge id)font };
  return CTLineCreateWithAttributedString((CFAttributedStringRef)[[NSAttributedString alloc] initWithString:text attributes:attr]);
}


void draw(CGContextRef ctx,
          CTLineRef textLine,
          CGFloat width,
          CGFloat height,
          CGFloat descent,
          CGFloat textWidth,
          CGFloat textHeight)
{
  // white background
  // CGContextSetRGBFillColor(ctx, 1.0, 1.0, 1.0, 1.0);
  // CGContextFillRect(ctx, {{0,0},{width,height}});

  // center text
  CGFloat x = ceilf((width - textWidth) / 2);
  CGFloat y = descent + ceilf((height - textHeight) / 2);

  // draw text
  CGContextSetTextPosition(ctx, x, y);
  CTLineDraw(textLine, ctx);
}


void makePDF(CTLineRef textLine,
             CGFloat width,
             CGFloat height,
             CGFloat descent,
             NSString* filename)
{
  // TODO: read and use options.width and options.height
  CFMutableDataRef consumerData = CFDataCreateMutable(kCFAllocatorDefault, 0);
  CGDataConsumerRef contextConsumer = CGDataConsumerCreateWithCFData(consumerData);
  assert(contextConsumer);
  const CGRect mediaBox{{0,0},{width,height}};
  auto ctx = CGPDFContextCreate(contextConsumer, &mediaBox, nil);
  assert(ctx);
  CGPDFContextBeginPage(ctx, nil);

  draw(ctx, textLine, width, height, descent, width, height);

  //  CGContextDrawPDFPage(ctx, page);
  CGPDFContextEndPage(ctx);
  CGPDFContextClose(ctx);
  CGContextRelease(ctx);
  [(__bridge NSData*)consumerData writeToFile:filename atomically:NO];
}


BOOL writePNG(CGImageRef image, NSString *filename) {
  CFURLRef url = (__bridge CFURLRef)[NSURL fileURLWithPath:filename];
  CGImageDestinationRef destination = CGImageDestinationCreateWithURL(url, kUTTypePNG, 1, NULL);
  if (!destination) {
    NSLog(@"Failed to create CGImageDestination for %@", filename);
    return NO;
  }

  CGImageDestinationAddImage(destination, image, nil);

  if (!CGImageDestinationFinalize(destination)) {
    NSLog(@"Failed to write image to %@", filename);
    CFRelease(destination);
    return NO;
  }

  CFRelease(destination);
  return YES;
}


void makePNG(CTLineRef textLine,
             CGFloat width,
             CGFloat height,
             CGFloat descent,
             NSString* filename)
{
  size_t widthz = (size_t)ceilf(width);
  size_t heightz = (size_t)ceilf(height * 1.2);  // 120% to make sure we don't clip
  if (options.width > 0) {
    widthz = options.width;
  }
  if (options.height > 0) {
    heightz = options.height;
  }

  void* data = malloc(widthz * heightz * 4);

  // Create the context and fill it with white background
  CGColorSpaceRef space = CGColorSpaceCreateDeviceRGB();
  CGBitmapInfo bitmapInfo = kCGImageAlphaPremultipliedLast;
  CGContextRef ctx = CGBitmapContextCreate(data, widthz, heightz, 8, widthz*4, space, bitmapInfo);
  CGColorSpaceRelease(space);

  draw(ctx, textLine, (CGFloat)widthz, (CGFloat)heightz, descent, width, height);

  CGImageRef imageRef = CGBitmapContextCreateImage(ctx);
  writePNG(imageRef, filename);

  free(data);
  CGImageRelease(imageRef);
  CGContextRelease(ctx);
}


void pdfmake(NSString* fontfile) {
  NSString* outfile = options.output;
  if (outfile == nil) {
    // default to fontfile.pdf
    outfile = [fontfile.stringByDeletingPathExtension stringByAppendingPathExtension:@"pdf"];
  }

  // Create an attributed string with string and font information
  CTFontRef font = loadFont(fontfile, options.size);

  CTLineRef textLine = createTextLine(font, options.text);
  if (!textLine) {
    fprintf(stderr, "%s: invalid sample text\n", prog);
    exit(1);
  }

  // get font metrics
  CGFloat ascent, descent, leading;
  CGFloat width = CTLineGetTypographicBounds(textLine, &ascent, &descent, &leading);
  CGFloat height = ascent + descent + leading;

  printf("write %s\n", outfile.UTF8String);
  if ([outfile.pathExtension.lowercaseString isEqualToString:@"png"]) {
    makePNG(textLine, width, height, descent, outfile);
  } else {
    makePDF(textLine, width, height, descent, outfile);
  }

  CFRelease(textLine);
  CFRelease(font);
}


void badarg(const char* msg, const char* arg) {
  fprintf(stderr, "%s: %s %s\n", prog, msg, arg);
  usage();
  exit(1);
}


const char* getargval(const char* arg, int argi, int argc, const char * argv[]) {
  int i = argi + 1;
  if (i == argc || strlen(argv[i]) == 0 || argv[i][0] == '-') {
    fprintf(stderr, "%s: missing value for argument %s\n", prog, arg);
    usage();
    exit(1);
  }
  return argv[i];
}


NSMutableArray<NSString*>* parseargs(int argc, const char * argv[]) {
  auto args = [NSMutableArray<NSString*> new];
  if (argc == 0) {
    fprintf(stderr, "invalid arguments\n");
    exit(0);
  }
  prog = argv[0];
  for (int i = 1; i < argc; i++) {
    auto arg = argv[i];
    if (strlen(arg) > 1 && arg[0] == '-') {
      if (strcmp(arg, "-h") == 0 || strcmp(arg, "-help") == 0) {
        usage();
        exit(0);
      }
      if (strcmp(arg, "-o") == 0) {
        auto val = getargval(arg, i++, argc, argv);
        options.output = [NSString stringWithUTF8String:val];

      } else if (strcmp(arg, "-width") == 0) {
        auto val = getargval(arg, i++, argc, argv);
        char* endptr = NULL;
        options.width = (size_t)strtoull((const char*)val, &endptr, 10);

      } else if (strcmp(arg, "-height") == 0) {
        auto val = getargval(arg, i++, argc, argv);
        char* endptr = NULL;
        options.height = (size_t)strtoull((const char*)val, &endptr, 10);

      } else if (strcmp(arg, "-z") == 0 || strcmp(arg, "-size") == 0) {
        auto val = getargval(arg, i++, argc, argv);
        auto f = atof(val);
        if (isnan(f) || f < 1) {
          badarg("invalid number", val);
        }
        options.size = (CGFloat)f;

      } else if (strcmp(arg, "-t") == 0 || strcmp(arg, "-text") == 0) {
        auto val = getargval(arg, i++, argc, argv);
        options.text = [NSString stringWithUTF8String:val];

      } else {
        badarg("unknown flag", arg);
      }
      continue;
    }
    [args addObject:[NSString stringWithUTF8String:arg]];
  }
  return args;
}


int main(int argc, const char * argv[]) {
  @autoreleasepool {
    auto fontfiles = parseargs(argc, argv);

    if (fontfiles.count < 1) {
      fprintf(stderr, "%s: missing <fontfile>\n", prog);
      usage();
      return 1;
    } else if (fontfiles.count > 1) {
      fprintf(stderr, "%s: extraneous argument after <fontfile>\n", prog);
      usage();
      return 1;
    }

    pdfmake(fontfiles[0]);
  }
  return 0;
}
