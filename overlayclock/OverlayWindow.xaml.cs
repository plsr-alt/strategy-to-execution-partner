using System;
using System.Runtime.InteropServices;
using System.Windows;
using System.Windows.Interop;
using overlayclock.ViewModels;

namespace overlayclock
{
    public partial class OverlayWindow : Window
    {
        private const int GWL_EXSTYLE = -20;
        private const int WS_EX_LAYERED = 0x00080000;
        private const int WS_EX_TRANSPARENT = 0x00000020;
        private const int WS_EX_TOOLWINDOW = 0x00000080;

        [DllImport("user32.dll", SetLastError = true)]
        private static extern int GetWindowLong(IntPtr hWnd, int nIndex);

        [DllImport("user32.dll")]
        private static extern int SetWindowLong(IntPtr hWnd, int nIndex, int dwNewLong);

        [DllImport("user32.dll")]
        private static extern bool RegisterHotKey(IntPtr hWnd, int id, uint fsModifiers, uint vk);

        [DllImport("user32.dll")]
        private static extern bool UnregisterHotKey(IntPtr hWnd, int id);

        private const int HOTKEY_ID = 9000;
        private const uint MOD_ALT = 0x0001;
        private const uint MOD_CONTROL = 0x0002;
        private const uint VK_T = 0x54; // T key
        private const int WM_HOTKEY = 0x0312;

        private bool _isClickThroughEnabled = true;
        private TimerViewModel _viewModel;
        private IntPtr _hwnd;
        private HwndSource? _hwndSource;

        public OverlayWindow(TimerViewModel viewModel)
        {
            InitializeComponent();
            _viewModel = viewModel;
            this.DataContext = _viewModel;
        }

        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
            // 画面の右上に配置
            this.Left = SystemParameters.WorkArea.Width - this.Width;
            this.Top = 0;
            
            _hwnd = new WindowInteropHelper(this).Handle;
            
            // クリック透過を有効化
            SetClickThrough(_isClickThroughEnabled);

            // グローバルショートカット登録 (Ctrl + Alt + T) で透過切り替え
            RegisterHotKey(_hwnd, HOTKEY_ID, MOD_CONTROL | MOD_ALT, VK_T);

            _hwndSource = HwndSource.FromHwnd(_hwnd);
            _hwndSource?.AddHook(HwndHook);
        }

        private IntPtr HwndHook(IntPtr hwnd, int msg, IntPtr wParam, IntPtr lParam, ref bool handled)
        {
            // ホットキーが押されたか判定
            if (msg == WM_HOTKEY && wParam.ToInt32() == HOTKEY_ID)
            {
                _isClickThroughEnabled = !_isClickThroughEnabled;
                SetClickThrough(_isClickThroughEnabled);
                handled = true;
            }
            return IntPtr.Zero;
        }

        public void SetClickThrough(bool enabled)
        {
            int extendedStyle = GetWindowLong(_hwnd, GWL_EXSTYLE);

            if (enabled)
            {
                SetWindowLong(_hwnd, GWL_EXSTYLE, extendedStyle | WS_EX_LAYERED | WS_EX_TRANSPARENT | WS_EX_TOOLWINDOW);
            }
            else
            {
                SetWindowLong(_hwnd, GWL_EXSTYLE, (extendedStyle | WS_EX_LAYERED | WS_EX_TOOLWINDOW) & ~WS_EX_TRANSPARENT);
            }
        }

        protected override void OnClosed(EventArgs e)
        {
            if (_hwndSource != null)
            {
                _hwndSource.RemoveHook(HwndHook);
                _hwndSource = null;
            }
            UnregisterHotKey(_hwnd, HOTKEY_ID);
            base.OnClosed(e);
        }
    }
}
