using System;
using System.Windows;
using overlayclock.Services;
using overlayclock.ViewModels;

namespace overlayclock
{
    public partial class App : Application
    {
        private System.Windows.Forms.NotifyIcon? _notifyIcon;
        private OverlayWindow? _overlayWindow;
        private TimerViewModel? _viewModel;
        private PomodoroService? _pomodoroService;

        protected override void OnStartup(StartupEventArgs e)
        {
            base.OnStartup(e);

            _pomodoroService = new PomodoroService();
            _viewModel = new TimerViewModel(_pomodoroService);

            // Startup with OverlayWindow only, no other windows
            _overlayWindow = new OverlayWindow(_viewModel);
            _overlayWindow.Show();

            InitializeNotifyIcon();
        }

        private void InitializeNotifyIcon()
        {
            _notifyIcon = new System.Windows.Forms.NotifyIcon();
            _notifyIcon.Icon = System.Drawing.SystemIcons.Application; // Default system icon
            _notifyIcon.Visible = true;
            _notifyIcon.Text = "OverlayClock Focus Timer";

            var contextMenu = new System.Windows.Forms.ContextMenuStrip();
            
            var startItem = new System.Windows.Forms.ToolStripMenuItem("Start");
            startItem.Click += (s, args) => _viewModel?.Start();
            
            var pauseResumeItem = new System.Windows.Forms.ToolStripMenuItem("Pause/Resume");
            pauseResumeItem.Click += (s, args) => {
                if (_pomodoroService?.CurrentPhase == Models.PomodoroPhase.Paused)
                    _pomodoroService.Resume();
                else if (_pomodoroService?.CurrentPhase != Models.PomodoroPhase.Idle)
                    _pomodoroService?.Pause();
                else
                    _pomodoroService?.Start();
            };

            var skipItem = new System.Windows.Forms.ToolStripMenuItem("Skip");
            skipItem.Click += (s, args) => _viewModel?.Skip();

            var exitItem = new System.Windows.Forms.ToolStripMenuItem("Exit");
            exitItem.Click += (s, args) => ExitApplication();

            contextMenu.Items.Add(startItem);
            contextMenu.Items.Add(pauseResumeItem);
            contextMenu.Items.Add(skipItem);
            contextMenu.Items.Add(new System.Windows.Forms.ToolStripSeparator());
            contextMenu.Items.Add(exitItem);

            _notifyIcon.ContextMenuStrip = contextMenu;

            // Optional: update text dynamically
            contextMenu.Opening += (s, args) => {
                if (_pomodoroService?.CurrentPhase == Models.PomodoroPhase.Paused)
                    pauseResumeItem.Text = "Resume";
                else
                    pauseResumeItem.Text = "Pause";
            };
        }

        private void ExitApplication()
        {
            if (_notifyIcon != null)
            {
                _notifyIcon.Visible = false;
                _notifyIcon.Dispose();
            }
            _pomodoroService?.Pause();
            _overlayWindow?.Close();
            Shutdown();
        }

        protected override void OnExit(ExitEventArgs e)
        {
            if (_notifyIcon != null)
            {
                _notifyIcon.Visible = false;
                _notifyIcon.Dispose();
            }
            base.OnExit(e);
        }
    }
}
