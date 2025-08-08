use std::{
    collections::VecDeque,
    io::{BufRead, BufReader, Write},
    process::{Child, Command, Stdio},
    sync::mpsc::{self, Receiver, Sender},
    thread,
    time::{Duration, Instant},
    
};

#[derive(Debug, Clone)]
pub enum PythonMessage {
    Output(String),
    Error(String),
    ProcessExit(i32),
}

pub struct App {
    // 기본 정보
    pub program_name: String,
    pub current_location: String,
    
    // Python 프로세스 관리
    pub python_process: Option<Child>,
    pub stdin_sender: Option<Sender<String>>,
    pub output_receiver: Option<Receiver<PythonMessage>>,
    
    // 출력 관리
    pub output_lines: Vec<String>,
    pub scroll_offset: usize,
    pub max_display_lines: usize,
    
    // 타이핑 효과
    pub typing_text: String,
    pub typing_target: String,
    pub typing_index: usize,
    pub last_type_time: Instant,
    pub typing_speed: Duration,
    pub is_typing: bool,
    
    // 입력 관리
    pub input_history: VecDeque<String>,
    pub current_input: String,
    pub cursor_position: usize,
    
    // 상태 정보
    pub user_status: String,
    pub equipment_status: String,
    pub is_python_running: bool,
    pub is_manually_scrolled: bool
}

impl App {
    pub fn new() -> Self {
        Self {
            program_name: "🎲 LLM D&D Adventure".to_string(),
            current_location: "게임 시작 준비중...".to_string(),
            
            python_process: None,
            stdin_sender: None,
            output_receiver: None,
            
            output_lines: Vec::new(),
            scroll_offset: 0,
            max_display_lines: 25,
            
            typing_text: String::new(),
            typing_target: String::new(),
            typing_index: 0,
            last_type_time: Instant::now(),
            typing_speed: Duration::from_millis(10), // 30ms per character
            is_typing: false,
            
            input_history: VecDeque::new(),
            current_input: String::new(),
            cursor_position: 0,
            
            user_status: "게임 준비중...".to_string(),
            equipment_status: "장비 준비중...".to_string(),
            is_python_running: false,
            is_manually_scrolled: false,
        }
    }

    pub fn start_python(&mut self, script_path: &str) -> Result<(), Box<dyn std::error::Error>> {
        // Python 프로세스 시작 - 버퍼링 비활성화 옵션 추가
        let mut child = Command::new("python3")
            .arg("-u")  // 중요: stdout/stderr 버퍼링 비활성화
            .arg("-W")  // 경고 표시
            .arg("ignore")  // 경고 무시
            .arg(script_path)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .env("PYTHONUNBUFFERED", "1")  // 환경변수로도 버퍼링 비활성화
            .env("PYTHONIOENCODING", "utf-8")  // UTF-8 인코딩 강제
            .spawn()?;

        let stdin = child.stdin.take().unwrap();
        let stdout = child.stdout.take().unwrap();
        let stderr = child.stderr.take().unwrap();

        // 채널 생성
        let (output_sender, output_receiver) = mpsc::channel();
        let (stdin_sender, stdin_receiver) = mpsc::channel::<String>();

        // stdout 읽기 스레드
        let output_sender_clone = output_sender.clone();
        thread::spawn(move || {
            let reader = BufReader::new(stdout);
            for line in reader.lines() {
                match line {
                    Ok(content) => {
                        if output_sender_clone.send(PythonMessage::Output(content)).is_err() {

                            break;
                        }
                        //thread::sleep(Duration::from_millis(500));
                    }
                    Err(_) => break,
                }
            }
        });

        // stderr 읽기 스레드
        let output_sender_clone = output_sender.clone();
        thread::spawn(move || {
            let reader = BufReader::new(stderr);
            for line in reader.lines() {
                match line {
                    Ok(content) => {
                        if output_sender_clone.send(PythonMessage::Error(content)).is_err() {
                            break;
                        }
                    }
                    Err(_) => break,
                }
            }
        });

        // stdin 쓰기 스레드
        thread::spawn(move || {
            let mut stdin = stdin;
            while let Ok(input) = stdin_receiver.recv() {
                if let Err(_) = writeln!(stdin, "{}", input) {
                    break;
                }
                if let Err(_) = stdin.flush() {
                    break;
                }
            }
        });

        self.python_process = Some(child);
        self.stdin_sender = Some(stdin_sender);
        self.output_receiver = Some(output_receiver);
        self.is_python_running = true;
        
        self.add_system_message("🐍 D&D 게임 시작! Python 엔진 가동중...");
        self.current_location = "게임 초기화 중...".to_string();

        Ok(())
    }

    pub fn update_output(&mut self) {
        // borrowing 문제 해결을 위해 메시지들을 먼저 수집
        let mut messages = Vec::new();
        
        if let Some(receiver) = &self.output_receiver {
            while let Ok(message) = receiver.try_recv() {
                messages.push(message);
            }
        }
        
        // 수집된 메시지들을 처리
        for message in messages {
            match message {
                PythonMessage::Output(line) => {
                    // typing 효과 켠
                    self.start_typing_effect(line);

                    // 그냥 출력 
                    //self.add_system_message(&line);
                }
                PythonMessage::Error(line) => {
                    self.add_system_message(&format!("🔥 ERROR: {}", line));
                }
                PythonMessage::ProcessExit(code) => {
                    self.add_system_message(&format!("🏁 게임 종료 (코드: {})", code));
                    self.is_python_running = false;
                }
            }
        }
    }

    pub fn start_typing_effect(&mut self, text: String) {
        if !text.trim().is_empty() {
            // 추가 
            if self.is_typing && !self.typing_target.is_empty(){
                self.output_lines.push(self.typing_target.clone());
                self.auto_scroll();
            }
            //
            self.typing_target = text;
            self.typing_text.clear();
            self.typing_index = 0;
            self.is_typing = true;
            self.last_type_time = Instant::now();
        }
    }

    pub fn update_typing_effect(&mut self) -> bool {
        if !self.is_typing {
            return false;
        }

        if self.last_type_time.elapsed() >= self.typing_speed {
            if self.typing_index < self.typing_target.len() {
                let chars: Vec<char> = self.typing_target.chars().collect();
                if self.typing_index < chars.len() {
                    self.typing_text.push(chars[self.typing_index]);
                    self.typing_index += 1;
                }
                self.last_type_time = Instant::now();
                return true;
            } else {
                // 타이핑 완료
                self.output_lines.push(self.typing_target.clone());
                self.typing_text.clear();
                self.typing_target.clear();
                self.is_typing = false;
                //self.auto_scroll();

                self.scroll_to_bottom();
                return true;
            }
        }
        false
    }

    fn scroll_to_bottom(&mut self){
        if !self.is_manually_scrolled{
            if self.output_lines.len() > self.max_display_lines {
                self.scroll_offset = self.output_lines.len() - self.max_display_lines;
            } else {
                self.scroll_offset = 0;
            }
        }
    }

    pub fn add_system_message(&mut self, message: &str) {
        self.output_lines.push(message.to_string());
        self.auto_scroll();
    }

    pub fn get_display_text(&self) -> String {
        if self.is_typing && !self.typing_text.is_empty() {
            //
            let recent_lines = self.get_recent_lines_for_typing();
            //format!("{}\n{}_", self.get_visible_lines(), self.typing_text)
            format!("{}\n{}_", recent_lines, self.typing_text)
        } else {
            self.get_visible_lines()
        }
    }

    fn get_recent_lines_for_typing(&self) -> String {
        let available_lines = self.max_display_lines.saturating_sub(1);
        let start = self.output_lines.len().saturating_sub(available_lines);

        self.output_lines[start..].join("\n")
    }

    fn get_visible_lines(&self) -> String {
        let start = self.scroll_offset;
        let end = (start + self.max_display_lines).min(self.output_lines.len());
        
        self.output_lines[start..end].join("\n")
    }

    fn auto_scroll(&mut self) {
        if self.output_lines.len() > self.max_display_lines {
            self.scroll_offset = self.output_lines.len() - self.max_display_lines;
        }
    }

    pub fn scroll_up(&mut self) {
        if self.scroll_offset > 0 {
            self.scroll_offset -= 1;
            self.is_manually_scrolled = true;
        }
    }

    pub fn scroll_down(&mut self) {
        let max_scroll = self.output_lines.len().saturating_sub(self.max_display_lines);
        if self.scroll_offset < max_scroll {
            self.scroll_offset += 1;

            if self.scroll_offset == max_scroll{
                self.is_manually_scrolled = false;
            }
        }
    }

    pub fn send_input(&mut self) {
        if !self.current_input.trim().is_empty() {
            let input = self.current_input.clone();
            
            // 입력 히스토리에 추가
            self.input_history.push_back(input.clone());
            if self.input_history.len() > 20 {
                self.input_history.pop_front();
            }
            
            // 사용자 입력을 화면에 표시
            self.add_system_message(&format!("👤 {}", input));
            
            // Python에 전송 (borrowing 문제 해결)
            if let Some(sender) = &self.stdin_sender {
                if sender.send(input).is_err() {
                    self.add_system_message("❌ Python 프로세스와의 연결이 끊어졌습니다.");
                    self.is_python_running = false;
                }
            }
        }
        
        self.current_input.clear();
        self.cursor_position = 0;
    }

    pub fn handle_char(&mut self, c: char) {
        //self.current_input.insert(self.cursor_position, c);
        //self.cursor_position += 1;

        // 안전한 문자 삽입 : 문자 경계에서만 삽입
        let chars: Vec<char> = self.current_input.chars().collect();
        let mut new_chars = chars;
        
        // cursor_position이 유효한지 확인
        if self.cursor_position <= new_chars.len(){
            new_chars.insert(self.cursor_position,c);
            self.current_input = new_chars.into_iter().collect();
            self.cursor_position += 1; 
        }
    }

    pub fn handle_backspace(&mut self) {
        if self.cursor_position > 0 {
            //self.cursor_position -= 1;
            //self.current_input.remove(self.cursor_position);
            let mut chars: Vec<char> = self.current_input.chars().collect();

            if self.cursor_position <= chars.len() {
                self.cursor_position -= 1;
                chars.remove(self.cursor_position);
                self.current_input = chars.into_iter().collect();
            }
        }
    }

    pub fn handle_left(&mut self) {
        if self.cursor_position > 0 {
            self.cursor_position -= 1;
        }
    }

    pub fn handle_right(&mut self) {
        let char_count = self.current_input.chars().count();
        if self.cursor_position < char_count {
            self.cursor_position += 1;
        }
    }

    pub fn get_input_history_display(&self) -> String {
        if self.input_history.is_empty() {
            "입력 기록이 없습니다.".to_string()
        } else {
            self.input_history
                .iter()
                .rev()
                .take(5) // 최근 5개만 표시
                .enumerate()
                .map(|(i, cmd)| format!("{}. {}", 5 - i, cmd))
                .collect::<Vec<_>>()
                .join("\n")
        }
    }

    pub fn stop_python(&mut self) {
        if let Some(mut process) = self.python_process.take() {
            let _ = process.kill();
            let _ = process.wait();
        }
        self.stdin_sender = None;
        self.output_receiver = None;
        self.is_python_running = false;
    }

    pub fn update_game_status(&mut self) {
        // 게임 상태에 따른 상태 업데이트 로직
        if self.is_python_running {
            self.user_status = "🎮 게임 진행 중 | 모험가 준비됨".to_string();
            self.equipment_status = "⚔️ 장비: 준비 완료 | 📦 인벤토리: 정상".to_string();
        } else {
            self.user_status = "⏸️ 게임 일시정지".to_string();
            self.equipment_status = "❌ 연결 끊김".to_string();
        }
    }
}