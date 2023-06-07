# !/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Build DEB package.
"""

import sys
import os
import os.path
import subprocess
import platform

try:
    import rich.console
except ImportError:
    print(u'Import error. Not found rich library')
    print(u'For install: pip3 install rich')
    sys.exit(2)

__version__ = (0, 0, 1, 1)
__author__ = 'xhermit'

DEBUG_MODE = True

CONSOLE = rich.console.Console()


def debug(message=u'', is_force_print=False):
    """
    Display debug information.

    :param message: Text message.
    :param is_force_print: Forcibly display.
    """
    if DEBUG_MODE or is_force_print:
        CONSOLE.print(str(message), style='blue')


def info(message=u'', is_force_print=False):
    """
    Print information.

    :param message: Text message.
    :param is_force_print: Forcibly display.
    """
    if DEBUG_MODE or is_force_print:
        CONSOLE.print(str(message), style='green')


def error(message=u'', is_force_print=False):
    """
    Print error message.

    :param message: Text message.
    :param is_force_print: Forcibly display.
    """
    if DEBUG_MODE or is_force_print:
        CONSOLE.print(str(message), style='bold red')


def warning(message=u'', is_force_print=False):
    """
    Print warning message.

    :param message: Text message.
    :param is_force_print: Forcibly display.
    """
    if DEBUG_MODE or is_force_print:
        CONSOLE.print(str(message), style='bold yellow')


def fatal(message=u'', is_force_print=False):
    """
    Print critical error message.

    :param message: Text message.
    :param is_force_print: Forcibly display.
    """
    if DEBUG_MODE or is_force_print:
        error(message, is_force_print=is_force_print)
        CONSOLE.print_exception(extra_lines=8, show_locals=True)


def getPlatform():
    """
    Get platform name.
    """
    return platform.uname()[0].lower()


def isWindowsPlatform():
    return getPlatform() == 'windows'


def isLinuxPlatform():
    return getPlatform() == 'linux'


def getOSVersion():
    """
    Get OS version.
    """
    try:
        if isLinuxPlatform():
            import distro
            return distro.linux_distribution()
        elif isWindowsPlatform():
            try:
                cmd = 'wmic os get Caption'
                p = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE)
            except FileNotFoundError:
                fatal('WMIC.exe was not found. Make sure \'C:\Windows\System32\wbem\' is added to PATH')
                return None

            stdout, stderror = p.communicate()

            output = stdout.decode('UTF-8', 'ignore')
            lines = output.split('\r\r')
            lines = [line.replace('\n', '').replace('  ', '') for line in lines if len(line) > 2]
            return lines[-1]
    except:
        fatal(u'Error get OS version')
    return None


def getPlatformKernel():
    """
    Get kernel.
    """
    try:
        return platform.release()
    except:
        fatal(u'Error get platform kernel')
    return None


def getCPUSpec():
    """
    Get CPU specification.
    """
    try:
        return platform.processor()
    except:
        fatal(u'Error get CPU specification')
    return None


def is64Linux():
    """
    Determine the bit depth of Linux.

    @return: True - 64 Linux. False - no.
    """
    cpu_spec = getCPUSpec()
    return cpu_spec == 'x86_64'


def saveTextFile(txt_filename, txt='', rewrite=True):
    """
    Save text file.

    :param txt_filename: Text file name.
    :param txt: Body text file as unicode.
    :param rewrite: Rewrite file if it exists?
    :return: True/False.
    """
    if not isinstance(txt, str):
        txt = str(txt)

    file_obj = None
    try:
        if rewrite and os.path.exists(txt_filename):
            os.remove(txt_filename)
            info(u'Remove file <%s>' % txt_filename)
        if not rewrite and os.path.exists(txt_filename):
            warning(u'File <%s> not saved' % txt_filename)
            return False

        # Check path
        txt_dirname = os.path.dirname(txt_filename)
        if not os.path.exists(txt_dirname):
            os.makedirs(txt_dirname)

        file_obj = open(txt_filename, 'wt')
        file_obj.write(txt)
        file_obj.close()
        return True
    except:
        if file_obj:
            file_obj.close()
        fatal('Save text file <%s> error' % txt_filename)
    return False


PACKAGENAME = 'main-menu'
PACKAGE_VERSION = '1.1'
LINUX_VERSION = '-'.join([str(x).lower() for x in getOSVersion()[:-1]])
LINUX_PLATFORM = 'all'  # 'amd64' if is64Linux() else 'i386'
DEPENDS = ', '.join(())
COPYRIGHT = '<xhermitone@gmail.com>'
DESCRIPTION = 'Main linux terminal menu'

DEBIAN_CONTROL_FILENAME = './deb/DEBIAN/control'
DEBIAN_CONTROL_BODY = f'''Package: {PACKAGENAME}
Version: {PACKAGE_VERSION}
Architecture: {LINUX_PLATFORM}
Maintainer: {COPYRIGHT}
Depends: {DEPENDS}
Section: contrib/otherosfs
Priority: optional
Description: {DESCRIPTION} 
'''

DEBIAN_PREINST_FILENAME = './deb/DEBIAN/preinst'
DEBIAN_PRERM_FILENAME = './deb/DEBIAN/prerm'
DEBIAN_POSTINST_FILENAME = './deb/DEBIAN/postinst'
DEBIAN_POSTRM_FILENAME = './deb/DEBIAN/postrm'


PRG_FILENAME = 'main_menu.py'


def sys_cmd(cmd):
    """
    Run system command.
    """
    info('System command: <%s>' % cmd)
    os.system(cmd)


def build_deb():
    """
    Build debian package.
    """
    if not os.path.exists('./deb/DEBIAN'):
        os.makedirs('./deb/DEBIAN')
    # if not os.path.exists(f'./deb/opt/{PACKAGENAME}'):
    #    os.makedirs(f'./deb/opt/{PACKAGENAME}')
    if not os.path.exists('./deb/usr/bin'):
        os.makedirs('./deb/usr/bin')

    saveTextFile(DEBIAN_CONTROL_FILENAME, DEBIAN_CONTROL_BODY)

    src_prg_filename = './%s' % PRG_FILENAME
    dst_prg_filename = os.path.splitext(os.path.basename(PRG_FILENAME))[0]
    if os.path.exists(src_prg_filename):
        sys_cmd('rm ./deb/usr/bin/*')
        sys_cmd('cp %s ./deb/usr/bin/%s' % (src_prg_filename, dst_prg_filename))
        sys_cmd('chmod 755 ./deb/usr/bin/%s' % dst_prg_filename)
    else:
        error('File <%s> not found' % src_prg_filename)

    # if not os.path.exists('./deb/usr/share/%s' % dst_prg_filename):
    #     os.makedirs('./deb/usr/share/%s' % dst_prg_filename)
    # sys_cmd('cp -r ./TOOLS/* ./deb/usr/share/%s' % dst_prg_filename)

    sys_cmd('fakeroot dpkg-deb --build deb')

    if os.path.exists('./deb.deb'):
        deb_filename = '%s-%s-%s.%s.deb' % (PACKAGENAME, PACKAGE_VERSION, LINUX_VERSION, LINUX_PLATFORM)
        sys_cmd('mv ./deb.deb ./%s' % deb_filename)
    else:
        error('ERROR! DEB build error')


def build():
    """
    Запуск полной сборки.
    """
    import time

    start_time = time.time()
    # print_color_txt(__doc__,CYAN_COLOR_TEXT)
    # compile_and_link()
    sys_cmd('rm ./*.deb')
    build_deb()
    sys_cmd('ls *.deb')
    debug(__doc__)
    debug('Time: <%d>' % (time.time()-start_time))


if __name__ == '__main__':
    build()
