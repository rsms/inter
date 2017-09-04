import re

featureRE = re.compile(
    "^"            # start of line
    "\s*"          #
    "feature"      # feature
    "\s+"          #
    "(\w{4})"      # four alphanumeric characters
    "\s*"          #
    "\{"           # {
    , re.MULTILINE # run in multiline to preserve line seps
)

def splitFeaturesForFontLab(text):
    """
    >>> result = splitFeaturesForFontLab(testText)
    >>> result == expectedTestResult
    True
    """
    classes = ""
    features = []
    while text:
        m = featureRE.search(text)
        if m is None:
            classes = text
            text = ""
        else:
            start, end = m.span()
            # if start is not zero, this is the first match
            # and all previous lines are part of the "classes"
            if start > 0:
                assert not classes
                classes = text[:start]
            # extract the current feature
            featureName = m.group(1)
            featureText = text[start:end]
            text = text[end:]
            # grab all text before the next feature definition
            # and add it to the current definition
            if text:
                m = featureRE.search(text)
                if m is not None:
                    start, end = m.span()
                    featureText += text[:start]
                    text = text[start:]
                else:
                    featureText += text
                    text = ""
            # store the feature
            features.append((featureName, featureText))
    return classes, features

testText = """
@class1 = [a b c d];

feature liga {
    sub f i by fi;
} liga;

@class2 = [x y z];

feature salt {
    sub a by a.alt;
} salt; feature ss01 {sub x by x.alt} ss01;

feature ss02 {sub y by y.alt} ss02;

# feature calt {
#     sub a b' by b.alt;
# } calt;
"""

expectedTestResult = (
    "\n@class1 = [a b c d];\n",
    [
        ("liga", "\nfeature liga {\n    sub f i by fi;\n} liga;\n\n@class2 = [x y z];\n"),
        ("salt", "\nfeature salt {\n    sub a by a.alt;\n} salt; feature ss01 {sub x by x.alt} ss01;\n"),
        ("ss02", "\nfeature ss02 {sub y by y.alt} ss02;\n\n# feature calt {\n#     sub a b' by b.alt;\n# } calt;\n")
    ]
)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
