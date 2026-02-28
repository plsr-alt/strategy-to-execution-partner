using System;
using System.Windows.Threading;
using overlayclock.Models;

namespace overlayclock.Services
{
    public class PomodoroService
    {
        private DispatcherTimer _timer;
        private TimeSpan _remaining;
        private PomodoroPhase _currentPhase;
        private int _focusSessionCount;
        private PomodoroPhase _previousPhaseBeforePause;

        public event EventHandler? Tick;
        public event EventHandler? PhaseChanged;

        public TimeSpan Remaining => _remaining;
        public PomodoroPhase CurrentPhase => _currentPhase;
        public int FocusSessionCount => _focusSessionCount;

        // Configurations
        public TimeSpan FocusDuration { get; set; } = TimeSpan.FromMinutes(25);
        public TimeSpan ShortBreakDuration { get; set; } = TimeSpan.FromMinutes(5);
        public TimeSpan LongBreakDuration { get; set; } = TimeSpan.FromMinutes(15);
        public int SessionsBeforeLongBreak { get; set; } = 4;

        public PomodoroService()
        {
            _currentPhase = PomodoroPhase.Idle;
            _remaining = FocusDuration;

            _timer = new DispatcherTimer
            {
                Interval = TimeSpan.FromSeconds(1)
            };
            _timer.Tick += Timer_Tick;
        }

        private void Timer_Tick(object? sender, EventArgs e)
        {
            if (_remaining.TotalSeconds > 0)
            {
                _remaining = _remaining.Subtract(TimeSpan.FromSeconds(1));
                Tick?.Invoke(this, EventArgs.EventArgsEmpty);
            }
            else
            {
                SkipToNextPhase();
            }
        }

        public void Start()
        {
            if (_currentPhase == PomodoroPhase.Idle)
            {
                TransitionTo(PomodoroPhase.Focus);
            }
            else if (_currentPhase == PomodoroPhase.Paused)
            {
                Resume();
            }
            else
            {
                _timer.Start();
            }
        }

        public void Pause()
        {
            if (_currentPhase != PomodoroPhase.Paused && _currentPhase != PomodoroPhase.Idle)
            {
                _previousPhaseBeforePause = _currentPhase;
                _timer.Stop();
                _currentPhase = PomodoroPhase.Paused;
                PhaseChanged?.Invoke(this, EventArgs.EventArgsEmpty);
            }
        }

        public void Resume()
        {
            if (_currentPhase == PomodoroPhase.Paused)
            {
                _currentPhase = _previousPhaseBeforePause;
                _timer.Start();
                PhaseChanged?.Invoke(this, EventArgs.EventArgsEmpty);
            }
        }

        public void Reset()
        {
            _timer.Stop();
            _focusSessionCount = 0;
            _currentPhase = PomodoroPhase.Idle;
            _remaining = FocusDuration;
            PhaseChanged?.Invoke(this, EventArgs.EventArgsEmpty);
            Tick?.Invoke(this, EventArgs.EventArgsEmpty);
        }

        public void SkipToNextPhase()
        {
            _timer.Stop();

            if (_currentPhase == PomodoroPhase.Focus || (_currentPhase == PomodoroPhase.Paused && _previousPhaseBeforePause == PomodoroPhase.Focus))
            {
                _focusSessionCount++;
                if (_focusSessionCount % SessionsBeforeLongBreak == 0)
                {
                    TransitionTo(PomodoroPhase.LongBreak);
                }
                else
                {
                    TransitionTo(PomodoroPhase.ShortBreak);
                }
            }
            else
            {
                TransitionTo(PomodoroPhase.Focus);
            }
        }

        private void TransitionTo(PomodoroPhase newPhase)
        {
            _currentPhase = newPhase;
            switch (newPhase)
            {
                case PomodoroPhase.Focus:
                    _remaining = FocusDuration;
                    break;
                case PomodoroPhase.ShortBreak:
                    _remaining = ShortBreakDuration;
                    break;
                case PomodoroPhase.LongBreak:
                    _remaining = LongBreakDuration;
                    break;
                case PomodoroPhase.Idle:
                    _remaining = FocusDuration;
                    break;
            }

            PhaseChanged?.Invoke(this, EventArgs.EventArgsEmpty);
            Tick?.Invoke(this, EventArgs.EventArgsEmpty);
            if (newPhase != PomodoroPhase.Idle)
            {
                _timer.Start();
            }
        }
    }
}
