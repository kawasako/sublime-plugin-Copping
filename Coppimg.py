import sublime, sublime_plugin, os, re


# class ExampleEventListener(sublime_plugin.EventListener):
#   def on_activated_async(self, view):
#     sublime.error_message("hogeeeeeeeeee")

class PutCommand(sublime_plugin.TextCommand):
  def run(self, edit, txt):
    points = self.view.sel()
    for point in points:
      self.view.insert(edit, point.begin(), txt)

class ExampleCommand(sublime_plugin.WindowCommand):
  def run(self):

    folders = self.window.folders()
    files = []
    reg = re.compile(r".*\.png|\.gif|\.jpg$")

    def fild_all_files(directory):
      for root, dirs, files in os.walk(directory):
        yield root
        for file in files:
          yield os.path.join(root, file).replace(directory, "")

    def append_img_tag(index):
      img_data = self.getImageInfo(folders[0]+files[index])
      img_tag = '<img src="{src}" width="{width}" height="{height}" alt="">'
      img_tag = img_tag.replace('{src}', files[index]).replace('{width}', str(img_data[1])).replace('{height}', str(img_data[2]))
      self.window.active_view().run_command('put', { "txt": img_tag })
      # self.window.active_view().insert(edit, 0, img_data.width)
      print(img_data)

    for file in fild_all_files(folders[0]):
      match_obj = reg.search(file)
      if match_obj:
        files.append(file)

    self.window.show_quick_panel(files, append_img_tag)

  # http://stackoverflow.com/questions/8032642/how-to-obtain-image-size-using-standard-python-class-without-using-external-lib
  def getImageInfo(self, fname):
    import struct
    import imghdr

    fhandle = open(fname, 'rb')
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

