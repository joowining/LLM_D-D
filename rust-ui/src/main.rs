use crossterm::{
    event::{self, DisableMouseCapture, EnableMouseCapture, Event, KeyCode, KeyEventKind},
    execute,
    terminal::{disable_raw_mode, enable_raw_mode, EnterAlternateScreen, LeaveAlternateScreen},
};
use ratatui::{
    backend::CrosstermBackend,
    Terminal,
};
use std::{
    error::Error,
    env,
    io,
    time::{Duration, Instant},
};

mod app;
mod ui;

use app::App;

fn main() -> Result<(), Box<dyn Error>> {
    // Python 스크립트 경로 설정
    let args: Vec<String> = env::args().collect();
    let python_script = if args.len() > 1 {
        args[1].clone()
    } else {
        // 기본값: 상위 디렉토리의 /home/joowon/my_develop/LLM_DND/main.py
        "/home/joowon/my_develop/LLM_DND/main.py".to_string()
    };

    // 터미널 설정
    enable_raw_mode()?;
    let mut stdout = io::stdout();
    execute!(stdout, EnterAlternateScreen, EnableMouseCapture)?;
    let backend = CrosstermBackend::new(stdout);
    let mut terminal = Terminal::new(backend)?;

    // 앱 생성
    let mut app = App::new();
    
    // Python 스크립트 시작
    if let Err(e) = app.start_python(&python_script) {
        // 터미널 복원
        restore_terminal(&mut terminal)?;
        eprintln!("Python 스크립트 시작 실패: {}", e);
        eprintln!("사용법: cargo run [python_script_path]");
        eprintln!("예시: cargo run intro.py");
        return Ok(());
    }

    // 앱 실행
    let res = run_app(&mut terminal, app);

    // 터미널 복원
    restore_terminal(&mut terminal)?;

    if let Err(err) = res {
        println!("에러 발생: {err:?}");
    }

    Ok(())
}

fn run_app(terminal: &mut Terminal<CrosstermBackend<std::io::Stdout>>, mut app: App) -> io::Result<()> {
    let mut last_tick = Instant::now();
    let tick_rate = Duration::from_millis(50); // 50ms for smooth typing effect

    loop {
        // Python 출력 업데이트
        app.update_output();
        
        // 타이핑 효과 업데이트
        let _typing_updated = app.update_typing_effect();
        
        // 게임 상태 업데이트
        app.update_game_status();

        // 화면 그리기
        terminal.draw(|f| ui::ui(f, &mut app))?;

        // 이벤트 처리
        let timeout = if app.is_typing {
            Duration::from_millis(25)
        } else {
            tick_rate
                .checked_sub(last_tick.elapsed())
                .unwrap_or_else(|| Duration::from_secs(0))
        };

        if event::poll(timeout)? {
            if let Event::Key(key) = event::read()? {
                if key.kind == KeyEventKind::Press {
                    match key.code {
                        // 종료
                        KeyCode::Char('q') | KeyCode::Esc => {
                            app.stop_python();
                            return Ok(());
                        }
                        
                        // 강제 종료
                        KeyCode::Char('c') if key.modifiers.contains(crossterm::event::KeyModifiers::CONTROL) => {
                            app.stop_python();
                            return Ok(());
                        }
                        
                        // 입력 전송
                        KeyCode::Enter => {
                            app.send_input();
                        }

                        // 타이핑 건너뛰기 
                        KeyCode::Char(' ') if key.modifiers.contains(crossterm::event::KeyModifiers::CONTROL)=>{
                            app.skip_typing();
                        }

                         // 타이핑 속도 조절
                        KeyCode::Char('1') if key.modifiers.contains(crossterm::event::KeyModifiers::CONTROL) => {
                            app.set_typing_speed_fast();
                        }
                        KeyCode::Char('2') if key.modifiers.contains(crossterm::event::KeyModifiers::CONTROL) => {
                            app.set_typing_speed_normal();
                        }
                        KeyCode::Char('3') if key.modifiers.contains(crossterm::event::KeyModifiers::CONTROL) => {
                            app.set_typing_speed_slow();
                        }
                        
                        // 문자 입력
                        KeyCode::Char(c) => {
                            app.handle_char(c);
                        }
                        
                        // 백스페이스
                        KeyCode::Backspace => {
                            app.handle_backspace();
                        }
                        
                        // 커서 이동
                        KeyCode::Left => {
                            app.handle_left();
                        }
                        KeyCode::Right => {
                            app.handle_right();
                        }
                        
                        // 스크롤
                        KeyCode::Up => {
                            app.scroll_up();
                        }
                        KeyCode::Down => {
                            app.scroll_down();
                        }
                        
                        // 페이지 스크롤
                        KeyCode::PageUp => {
                            for _ in 0..5 {
                                app.scroll_up();
                            }
                        }
                        KeyCode::PageDown => {
                            for _ in 0..5 {
                                app.scroll_down();
                            }
                        }
                        
                        _ => {}
                    }
                }
            }
        }

        // 정기적인 업데이트를 위한 틱
        if last_tick.elapsed() >= tick_rate {
            last_tick = Instant::now();
        }

        // Python 프로세스 상태 확인
        if !app.is_python_running {
            if let Some(mut process) = app.python_process.take() {
                if let Ok(Some(_)) = process.try_wait() {
                    // 프로세스가 정상 종료됨
                    app.add_system_message("🏁 Python 게임 프로세스가 종료되었습니다.");
                    app.add_system_message("📌 q 또는 ESC를 눌러 TUI를 종료하세요.");
                }
            }
        }
    }
}

fn restore_terminal(terminal: &mut Terminal<CrosstermBackend<io::Stdout>>) -> Result<(), Box<dyn Error>> {
    disable_raw_mode()?;
    execute!(
        terminal.backend_mut(),
        LeaveAlternateScreen,
        DisableMouseCapture
    )?;
    terminal.show_cursor()?;
    println!("🎮 D&D 게임을 종료합니다. 모험을 마쳐주셔서 감사합니다!");
    Ok(())
}