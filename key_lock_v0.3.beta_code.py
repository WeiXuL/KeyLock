import wx
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from Crypto.Random import get_random_bytes
import os

# 从文件中加载密钥
def load_key(key_file):
    with open(key_file, 'rb') as f:
        key = f.read()
    return key

# 获取密码
def get_password():
    while True:
        dlg = wx.TextEntryDialog(None, "请输入密码（密码长度为16、24、32位）：", "输入密码")
        if dlg.ShowModal() == wx.ID_OK:
            password = dlg.GetValue()
            if len(password) >= 16:
                dlg.Destroy()
                return password
            else:
                wx.MessageBox("密码长度太短，请重新输入！", "错误", wx.OK | wx.ICON_ERROR)
        else:
            dlg.Destroy()
            return None

# 生成随机密钥
def generate_key(key_length):
    return get_random_bytes(key_length)

# 加密文件
def encrypt_file(input_file, output_file, key):
    cipher = AES.new(key, AES.MODE_ECB)

    with open(input_file, 'rb') as f:
        plaintext = f.read()
    padded_plaintext = pad(plaintext, AES.block_size)
    ciphertext = cipher.encrypt(padded_plaintext)
    with open(output_file, 'wb') as f:
        f.write(ciphertext)
    wx.MessageBox("文件已加密并保存到{}".format(output_file), "加密完成", wx.OK | wx.ICON_INFORMATION)

# 解密文件
def decrypt_file(input_file, output_file, key):
    cipher = AES.new(key, AES.MODE_ECB)

    with open(input_file, 'rb') as f:
        ciphertext = f.read()
    try:
        plaintext = cipher.decrypt(ciphertext)
        unpadded_plaintext = unpad(plaintext, AES.block_size)
        with open(output_file, 'wb') as f:
            f.write(unpadded_plaintext)
        wx.MessageBox("文件已解密并保存到{}".format(output_file), "解密完成", wx.OK | wx.ICON_INFORMATION)
    except ValueError:
        wx.MessageBox("密码错误，解密失败！", "错误", wx.OK | wx.ICON_ERROR)

# 使用密码生成密钥
def derive_key(password):
    return password.encode()

class KeyLockFrame(wx.Frame):
    def __init__(self):
        super(KeyLockFrame, self).__init__(None, title="Key-Lock 版本:V0.3.bata 版权所有:XeroL©", size=(450, 200))
        panel = wx.Panel(self)

        self.welcome_label = wx.StaticText(panel, label="欢迎使用 Key-Lock 文件加解密工具！", pos=(120, 20), size=(300, 25))
        self.choice_label = wx.StaticText(panel, label="请选择操作：", pos=(50, 50), size=(200, 25))
        self.gen_key_btn = wx.Button(panel, label="生成密钥", pos=(50, 80), size=(150, 30))
        self.enc_dec_btn = wx.Button(panel, label="加密/解密文件", pos=(250, 80), size=(150, 30))

        self.gen_key_btn.Bind(wx.EVT_BUTTON, self.on_generate_key)
        self.enc_dec_btn.Bind(wx.EVT_BUTTON, self.on_encrypt_decrypt)

        self.Show()

    def on_generate_key(self, event):
        dlg = GenerateKeyDialog(None, title="生成密钥")
        dlg.ShowModal()
        dlg.Destroy()

    def on_encrypt_decrypt(self, event):
        dlg = EncDecChoiceDialog(None, title="加密/解密文件")
        dlg.ShowModal()
        dlg.Destroy()

class GenerateKeyDialog(wx.Dialog):
    def __init__(self, *args, **kw):
        super(GenerateKeyDialog, self).__init__(None, title="生成密钥", size=(550, 200))

        self.key_length_label = wx.StaticText(self, label="密钥长度（16、24或32）：", pos=(20, 20))
        self.key_length_entry = wx.TextCtrl(self, pos=(200, 20), size=(150, 25))
        self.key_path_label = wx.StaticText(self, label="密钥保存路径：", pos=(20, 50))
        self.key_path_entry = wx.TextCtrl(self, pos=(200, 50), size=(200, 25))
        self.key_path_btn = wx.Button(self, label="选择文件夹", pos=(400, 50), size=(100, 25))
        self.key_filename_label = wx.StaticText(self, label="要保存的文件名：", pos=(20, 80))
        self.key_filename_entry = wx.TextCtrl(self, pos=(200, 80), size=(200, 25))
        self.submit_btn = wx.Button(self, label="提交", pos=(200, 120), size=(150, 30))

        self.key_path_btn.Bind(wx.EVT_BUTTON, self.on_select_path)
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)

        self.ShowModal()

    def on_select_path(self, event):
        dlg = wx.DirDialog(self, "选择密钥保存路径", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.key_path_entry.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_submit(self, event):
        key_length = int(self.key_length_entry.GetValue())
        key_path = self.key_path_entry.GetValue()
        key_filename = self.key_filename_entry.GetValue()
        key_file = os.path.join(key_path, key_filename)

        directory = os.path.dirname(key_file)
        if not os.path.exists(directory):
            os.makedirs(directory)

        key = generate_key(key_length)
        wx.MessageBox("生成的密钥参数如下：\n密钥长度（字节数）: {}\n密钥内容: {}".format(key_length, key), "生成密钥", wx.OK | wx.ICON_INFORMATION)

        with open(key_file, 'wb') as f:
            f.write(key)
        self.Destroy()

class EncDecChoiceDialog(wx.Dialog):
    def __init__(self, *args, **kw):
        super(EncDecChoiceDialog, self).__init__(None, title="加密/解密文件", size=(265, 200))

        self.enc_file_btn = wx.Button(self, label="加密文件", pos=(50, 20), size=(150, 30))
        self.dec_file_btn = wx.Button(self, label="解密文件", pos=(50, 100), size=(150, 30))

        self.enc_file_btn.Bind(wx.EVT_BUTTON, self.on_enc_file)
        self.dec_file_btn.Bind(wx.EVT_BUTTON, self.on_dec_file)

        self.ShowModal()

    def on_enc_file(self, event):
        dlg = EncFileChoiceDialog(None, title="加密文件")
        dlg.ShowModal()
        dlg.Destroy()

    def on_dec_file(self, event):
        dlg = DecFileChoiceDialog(None, title="解密文件")
        dlg.ShowModal()
        dlg.Destroy()

class EncFileChoiceDialog(wx.Dialog):
    def __init__(self, *args, **kw):
        super(EncFileChoiceDialog, self).__init__(None, title="加密文件", size=(220, 170))

        self.key_choice_label = wx.StaticText(self, label="请选择加密方式：", pos=(20, 20))
        self.key_choice_rbtn_key = wx.RadioButton(self, label="使用密钥", pos=(20, 50))
        self.key_choice_rbtn_password = wx.RadioButton(self, label="使用密码", pos=(20, 80))
        self.submit_btn = wx.Button(self, label="提交", pos=(120, 50), size=(70, 50))

        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)

        self.ShowModal()

    def on_submit(self, event):
        if self.key_choice_rbtn_key.GetValue():
            dlg = wx.FileDialog(self, "选择密钥文件路径", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_OK:
                key_file = dlg.GetPath()
                dlg = EncFileDialog(None, title="加密文件", key_file=key_file)
                dlg.ShowModal()
                dlg.Destroy()
            dlg.Destroy()
        elif self.key_choice_rbtn_password.GetValue():
            dlg = wx.TextEntryDialog(None, "请输入密码（请输入16、24、32位数）：", "输入密码", style=wx.TextEntryDialogStyle | wx.OK | wx.CANCEL)
            if dlg.ShowModal() == wx.ID_OK:
                password = dlg.GetValue()
                dlg = EncFileDialog(None, title="加密文件", password=password)
                dlg.ShowModal()
                dlg.Destroy()
            dlg.Destroy()
        self.Destroy()

class DecFileChoiceDialog(wx.Dialog):
    def __init__(self, *args, **kw):
        super(DecFileChoiceDialog, self).__init__(None, title="解密文件", size=(220, 170))

        self.key_choice_label = wx.StaticText(self, label="请选择解密方式：", pos=(20, 20))
        self.key_choice_rbtn_key = wx.RadioButton(self, label="使用密钥", pos=(20, 50))
        self.key_choice_rbtn_password = wx.RadioButton(self, label="使用密码", pos=(20, 80))
        self.submit_btn = wx.Button(self, label="提交", pos=(120, 50), size=(70, 50))

        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)

        self.ShowModal()

    def on_submit(self, event):
        if self.key_choice_rbtn_key.GetValue():
            dlg = wx.FileDialog(self, "选择密钥文件路径", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
            if dlg.ShowModal() == wx.ID_OK:
                key_file = dlg.GetPath()
                dlg = DecFileDialog(None, title="解密文件", key_file=key_file)
                dlg.ShowModal()
                dlg.Destroy()
            dlg.Destroy()
        elif self.key_choice_rbtn_password.GetValue():
            dlg = wx.TextEntryDialog(None, "请输入密码：", "输入密码", style=wx.TextEntryDialogStyle | wx.OK | wx.CANCEL)
            if dlg.ShowModal() == wx.ID_OK:
                password = dlg.GetValue()
                dlg = DecFileDialog(None, title="解密文件", password=password)
                dlg.ShowModal()
                dlg.Destroy()
            dlg.Destroy()
        self.Destroy()

class EncFileDialog(wx.Dialog):
    def __init__(self, *args, key_file=None, password=None, **kw):
        super(EncFileDialog, self).__init__(None, title="加密文件", size=(550, 200))

        self.input_file_label = wx.StaticText(self, label="请输入要加密的文件路径：", pos=(20, 20))
        self.input_file_entry = wx.TextCtrl(self, pos=(200, 20), size=(200, 25))
        self.input_file_btn = wx.Button(self, label="选择文件", pos=(420, 20), size=(100, 25))
        self.output_folder_label = wx.StaticText(self, label="请输入加密后的文件夹路径：", pos=(20, 50))
        self.output_folder_entry = wx.TextCtrl(self, pos=(200, 50), size=(200, 25))
        self.output_folder_btn = wx.Button(self, label="选择文件夹", pos=(420, 50), size=(100, 25))
        self.output_filename_label = wx.StaticText(self, label="请输入加密后的文件名：", pos=(20, 80))
        self.output_filename_entry = wx.TextCtrl(self, pos=(200, 80), size=(200, 25))
        self.submit_btn = wx.Button(self, label="提交", pos=(200, 120), size=(150, 30))

        self.input_file_btn.Bind(wx.EVT_BUTTON, self.on_select_input_file)
        self.output_folder_btn.Bind(wx.EVT_BUTTON, self.on_select_output_folder)
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)

        self.key_file = key_file
        self.password = password

        self.ShowModal()

    def on_select_input_file(self, event):
        dlg = wx.FileDialog(self, "选择要加密的文件", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.input_file_entry.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_select_output_folder(self, event):
        dlg = wx.DirDialog(self, "选择加密后的文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.output_folder_entry.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_submit(self, event):
        input_file = self.input_file_entry.GetValue()
        output_folder = self.output_folder_entry.GetValue()
        output_filename = self.output_filename_entry.GetValue()
        encrypted_file = os.path.join(output_folder, output_filename)

        if self.key_file:
            key = load_key(self.key_file)
        else:
            password = self.password
            if not password:
                wx.MessageBox("请输入密码！", "错误", wx.OK | wx.ICON_ERROR)
                return
            key = derive_key(password)

        encrypt_file(input_file, encrypted_file, key)
        self.Destroy()

class DecFileDialog(wx.Dialog):
    def __init__(self, *args, key_file=None, password=None, **kw):
        super(DecFileDialog, self).__init__(None, title="解密文件", size=(550, 200))

        self.input_file_label = wx.StaticText(self, label="请输入要解密的文件路径：", pos=(20, 20))
        self.input_file_entry = wx.TextCtrl(self, pos=(200, 20), size=(200, 25))
        self.input_file_btn = wx.Button(self, label="选择文件", pos=(420, 20), size=(100, 25))
        self.output_folder_label = wx.StaticText(self, label="请输入解密后的文件夹路径：", pos=(20, 50))
        self.output_folder_entry = wx.TextCtrl(self, pos=(200, 50), size=(200, 25))
        self.output_folder_btn = wx.Button(self, label="选择文件夹", pos=(420, 50), size=(100, 25))
        self.output_filename_label = wx.StaticText(self, label="请输入解密后的文件名：", pos=(20, 80))
        self.output_filename_entry = wx.TextCtrl(self, pos=(200, 80), size=(200, 25))
        self.submit_btn = wx.Button(self, label="提交", pos=(200, 120), size=(150, 30))

        self.input_file_btn.Bind(wx.EVT_BUTTON, self.on_select_input_file)
        self.output_folder_btn.Bind(wx.EVT_BUTTON, self.on_select_output_folder)
        self.submit_btn.Bind(wx.EVT_BUTTON, self.on_submit)

        self.key_file = key_file
        self.password = password

        self.ShowModal()

    def on_select_input_file(self, event):
        dlg = wx.FileDialog(self, "选择要解密的文件", style=wx.FD_OPEN | wx.FD_FILE_MUST_EXIST)
        if dlg.ShowModal() == wx.ID_OK:
            self.input_file_entry.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_select_output_folder(self, event):
        dlg = wx.DirDialog(self, "选择解密后的文件夹", style=wx.DD_DEFAULT_STYLE)
        if dlg.ShowModal() == wx.ID_OK:
            self.output_folder_entry.SetValue(dlg.GetPath())
        dlg.Destroy()

    def on_submit(self, event):
        input_file = self.input_file_entry.GetValue()
        output_folder = self.output_folder_entry.GetValue()
        output_filename = self.output_filename_entry.GetValue()
        decrypted_file = os.path.join(output_folder, output_filename)

        if self.key_file:
            key = load_key(self.key_file)
        else:
            password = self.password
            if not password:
                wx.MessageBox("请输入密码！", "错误", wx.OK | wx.ICON_ERROR)
                return
            key = derive_key(password)

        decrypt_file(input_file, decrypted_file, key)
        self.Destroy()

class KeyLockApp(wx.App):
    def OnInit(self):
        frame = KeyLockFrame()
        frame.Show(True)
        return True

if __name__ == "__main__":
    app = KeyLockApp()
    app.MainLoop()
