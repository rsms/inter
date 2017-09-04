"""
ROBOFAB
RoboFab is a Python library with objects
that deal with data usually associated
with fonts and type design.

DEVELOPERS
RoboFab is developed and maintained by
	Tal Leming
	Erik van Blokland
	Just van Rossum
	(in no particular order)

MORE INFO
The RoboFab homepage, documentation etc.
http://robofab.com

SVN REPOSITORY
http://svn.robofab.com
TRAC
http://code.robofab.com

RoboFab License Agreement

Copyright (c) 2003-2013, The RoboFab Developers:
	Erik van Blokland
	Tal Leming
	Just van Rossum

All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
Neither the name of the The RoboFab Developers nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
	
Up to date info on RoboFab:
	http://robofab.com/
	
This is the BSD license:
	http://www.opensource.org/licenses/BSD-3-Clause
	

HISTORY
RoboFab starts somewhere during the 
TypoTechnica in Heidelberg, 2003.

DEPENDENCIES
RoboFab expects fontTools to be installed.
http://sourceforge.net/projects/fonttools/
Some of the RoboFab modules require data files
that are included in the source directory.
RoboFab likes to be able to calculate paths 
to these data files all by itself, so keep them
together with the source files.

QUOTES
Yuri Yarmola:
"If data is somehow available to other programs
via some standard data-exchange interface which
can be accessed by some library in Python, you
can make a Python script that uses that library
to apply data to a font opened in FontLab."

W.A. Dwiggins:
"You will understand that I am not trying to
short-circuit any of your shop operations in
sending drawings of this kind. The closer I can
get to the machine the better the result.
Subtleties of curves are important, as you know,
and if I can make drawings that can be used in
the large size I have got one step closer to the
machine that cuts the punches." [1932]

"""

from .exceptions import RoboFabError, RoboFabWarning

numberVersion = (1, 2, "release", 1)
version = "1.2.1"
