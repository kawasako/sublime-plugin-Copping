import sublime, sublime_plugin, os, re

class Image2tagCommand(sublime_plugin.WindowCommand):
  def run(self):

    if not self.window.folders():
      sublime.status_message('Not opened directories.')
      return

    # Set selected index
    if not self.window.active_view().get_status('selected_index'):
      self.window.active_view().set_status('selected_index', '0')

    self.folder = self.window.folders()[0]
    self.close_message = '[×] Close this window'
    self.files = [self.close_message]
    reg = re.compile(r'.*\.png|\.gif|\.jpg$')

    for file in self.fild_all_files(self.folder):
      match_obj = reg.search(file)
      if match_obj:
        self.files.append(file)

    self.window.show_quick_panel(self.files, self.append_img_tag, 0, int(self.window.active_view().get_status('selected_index')))

  def fild_all_files(self, directory):
    for root, dirs, files in os.walk(directory):
      yield root
      for file in files:
        yield os.path.join(root, file).replace(directory, "")

  def append_img_tag(self, index):
    if 0 > index:
      sublime.status_message('Closed')
      return

    # Update selected index
    self.window.active_view().set_status('selected_index', str(index))

    if not self.files[index] == self.close_message:
      file_path = self.files[index]

      if sublime.load_settings('Image2tag.sublime-settings').get('relative_assets'):
        dir_reg = re.compile(r'^.*\/')
        base_dir = dir_reg.match(self.window.active_view().file_name()).group(0)
        file_path = self.folder+self.files[index]
        file_path = os.path.relpath(file_path, base_dir)
      elif sublime.load_settings('Image2tag.sublime-settings').get('root_path'):
        file_path = self.files[index].replace(sublime.load_settings('Image2tag.sublime-settings').get('root_path'), '', 1)

      syntax = self.window.active_view().settings().get('syntax')
      syntax = re.sub('^.*\/(.*)\.tmLanguage', r'\1', syntax)

      if sublime.load_settings('Image2tag.sublime-settings').has(syntax+'_tag'):
        img_tag = sublime.load_settings('Image2tag.sublime-settings').get(syntax+'_tag')
      else:
        img_tag = sublime.load_settings('Image2tag.sublime-settings').get('Default_tag')

      img_data = self.getImageInfo(self.folder+self.files[index])
      img_tag = img_tag.format(src=file_path, width=img_data[1], height=img_data[2])

      self.window.active_view().run_command('insert', {'characters': img_tag})

  # http://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib（Updated for Image2tag）
  def getImageInfo(self, fname):
    import struct
    import imghdr

    with open(fname, 'rb') as fhandle:
      head = fhandle.read(24)
      if len(head) != 24:
        return
      if imghdr.what(fname) == 'png':
        check = struct.unpack('>i', head[4:8])[0]
        if check != 0x0d0a1a0a:
          return
        width, height = struct.unpack('>ii', head[16:24])
      elif imghdr.what(fname) == 'gif':
        width, height = struct.unpack('<HH', head[6:10])
      elif imghdr.what(fname) == 'jpeg':
        try:
          fhandle.seek(0) # Read 0xff next
          size = 2
          ftype = 0
          while not 0xc0 <= ftype <= 0xcf:
            fhandle.seek(size, 1)
            byte = fhandle.read(1)
            while ord(byte) == 0xff:
              byte = fhandle.read(1)
            ftype = ord(byte)
            size = struct.unpack('>H', fhandle.read(2))[0] - 2
          # We are at a SOFn block
          fhandle.seek(1, 1) # Skip `precision' byte.
          height, width = struct.unpack('>HH', fhandle.read(4))
        except Exception: # IGNORE:W0703
          return
      else:
        return
    return None, width, height

