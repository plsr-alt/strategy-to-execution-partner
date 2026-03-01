using System;
using overlayclock.Models;
using overlayclock.Services;

namespace overlayclock.ViewModels
{
    public class TimerViewModel : ViewModelBase
    {
        private readonly PomodoroService _pomodoroService;

        public string RemainingText => $"{(int)_pomodoroService.Remaining.TotalMinutes:D2}:{_pomodoroService.Remaining.Seconds:D2}";
        
        public string PhaseText
        {
            get
            {
                return _pomodoroService.CurrentPhase switch
                {
                    PomodoroPhase.Idle => "READY",
                    PomodoroPhase.Focus => "FOCUS",
                    PomodoroPhase.ShortBreak => "SHORT BREAK",
                    PomodoroPhase.LongBreak => "LONG BREAK",
                    PomodoroPhase.Paused => "PAUSED",
                    _ => ""
                };
            }
        }

        // 0 to 1
        public double Progress
        {
            get
            {
                TimeSpan totalDuration = _pomodoroService.CurrentPhase switch
                {
                    PomodoroPhase.Focus => _pomodoroService.FocusDuration,
                    PomodoroPhase.ShortBreak => _pomodoroService.ShortBreakDuration,
                    PomodoroPhase.LongBreak => _pomodoroService.LongBreakDuration,
                    _ => _pomodoroService.FocusDuration
                };

                if (totalDuration.TotalSeconds == 0) return 0;
                
                // 1.0 when full, 0.0 when empty
                return _pomodoroService.Remaining.TotalSeconds / totalDuration.TotalSeconds;
            }
        }

        public TimerViewModel(PomodoroService pomodoroService)
        {
            _pomodoroService = pomodoroService;
            _pomodoroService.Tick += OnServiceTick;
            _pomodoroService.PhaseChanged += OnServicePhaseChanged;
        }

        private void OnServiceTick(object? sender, EventArgs e)
        {
            OnPropertyChanged(nameof(RemainingText));
            OnPropertyChanged(nameof(Progress));
        }

        private void OnServicePhaseChanged(object? sender, EventArgs e)
        {
            OnPropertyChanged(nameof(RemainingText));
            OnPropertyChanged(nameof(PhaseText));
            OnPropertyChanged(nameof(Progress));

            // 相対遷移時（Idle, Paused 以外の実フェーズへの遷移）に音を鳴らす
            var phase = _pomodoroService.CurrentPhase;
            if (phase == PomodoroPhase.Focus || phase == PomodoroPhase.ShortBreak || phase == PomodoroPhase.LongBreak)
            {
                System.Media.SystemSounds.Asterisk.Play();
            }
        }
        
        // For simplicity now, let's expose methods to test interactions if needed later
        public void Start() => _pomodoroService.Start();
        public void Skip() => _pomodoroService.SkipToNextPhase();
    }
}
