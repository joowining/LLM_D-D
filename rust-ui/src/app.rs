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
    
    // 타이핑 효과 - 큐 시스템으로 변경
    pub typing_queue: VecDeque<String>, // 타이핑할 텍스트들의 큐
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
    pub is_manually_scrolled: bool,
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
            
            typing_queue: VecDeque::new(),
            typing_text: String::new(),
            typing_target: String::new(),
            typing_index: 0,
            last_type_time: Instant::now(),
            typing_speed: Duration::from_millis(30),
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
        let mut child = Command::new("python3")
            .arg("-u")
            .arg("-W")
            .arg("ignore")
            .arg(script_path)
            .stdin(Stdio::piped())
            .stdout(Stdio::piped())
            .stderr(Stdio::piped())
            .env("PYTHONUNBUFFERED", "1")
            .env("PYTHONIOENCODING", "utf-8")
            .spawn()?;

        let stdin = child.stdin.take().unwrap();
        let stdout = child.stdout.take().unwrap();
        let stderr = child.stderr.take().unwrap();

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
        
        // 시스템 메시지는 즉시 표시
        self.add_system_message("🐍 D&D 게임 시작! Python 엔진 가동중...");
        self.current_location = "게임 초기화 중...".to_string();

        Ok(())
    }

    pub fn update_output(&mut self) {
        let mut messages = Vec::new();
        
        if let Some(receiver) = &self.output_receiver {
            while let Ok(message) = receiver.try_recv() {
                messages.push(message);
            }
        }
        
        for message in messages {
            match message {
                PythonMessage::Output(line) => {
                    // 파이썬 출력만 타이핑 효과 적용
                    //self.add_system_message(&line);
                    self.queue_typing_text(line);
                }
                PythonMessage::Error(line) => {
                    // 에러는 즉시 표시
                    self.add_system_message(&format!("🔥 ERROR: {}", line));
                }
                PythonMessage::ProcessExit(code) => {
                    // 프로세스 종료도 즉시 표시
                    self.add_system_message(&format!("🏁 게임 종료 (코드: {})", code));
                    self.is_python_running = false;
                }
            }
        }
    }

    pub fn queue_typing_text(&mut self, text: String){
        self.typing_queue.push_back(text);

        if !self.is_typing{
            self.start_next_typing();
        }
    }

    fn start_next_typing(&mut self){
        if let Some(text) = self.typing_queue.pop_front(){
            self.typing_target = text;
            self.typing_text.clear();
            self.typing_index = 0;
            self.is_typing = true;
            self.last_type_time = Instant::now();
        }else {
            self.is_typing = false;
        }
    }

    pub fn update_typing_effect(&mut self) -> bool{
        if !self.is_typing {
            return false;
        }

        let now = Instant::now();
        if now.duration_since(self.last_type_time) >= self.typing_speed {
            if self.typing_index < self.typing_target.chars().count(){
                let chars: Vec<char> = self.typing_target.chars().collect();
                if let Some(next_char) = chars.get(self.typing_index){
                    self.typing_text.push(*next_char);
                    self.typing_index += 1;
                    self.last_type_time = now;

                    if !self.is_manually_scrolled{
                        self.scroll_to_bottom();
                    }
                    return true;
                } 
            } else {
                self.output_lines.push(self.typing_target.clone());
                self.typing_text.clear();
                self.typing_target.clear();
                self.typing_index = 0;

                if !self.is_manually_scrolled{
                    self.scroll_to_bottom();
                }

                self.start_next_typing();
                return true;
            }
        }

        false 
    }


    fn ensure_auto_scroll(&mut self) {
        if !self.is_manually_scrolled {
            self.scroll_to_bottom();
        }
    }

    fn is_at_bottom(&self) -> bool {
        let total_lines = self.get_total_lines();
        if total_lines <= self.max_display_lines {
            return true;
        }
        let max_scroll = total_lines - self.max_display_lines;
        self.scroll_offset >= max_scroll
    }

    pub fn scroll_down(&mut self) {
        let total_lines = self.get_total_lines();
        let max_scroll = if total_lines > self.max_display_lines {
            total_lines - self.max_display_lines
        } else {
            0
        };

        if self.scroll_offset < max_scroll {
            self.scroll_offset += 1;
            
            // 맨 아래에 도달했다면 수동 스크롤 해제
            if self.scroll_offset >= max_scroll {
                self.is_manually_scrolled = false;
            }
        }
    }

    fn scroll_to_bottom_force(&mut self) {
        if self.output_lines.len() > self.max_display_lines {
            self.scroll_offset = self.output_lines.len() - self.max_display_lines;
        } else {
            self.scroll_offset = 0;
        }
    }

    // 시스템 메시지는 즉시 표시 (타이핑 효과 없음)
    pub fn add_system_message(&mut self, message: &str) {
        self.output_lines.push(message.to_string());
        self.ensure_auto_scroll();
    }

    pub fn get_display_text(&self) -> String {
        let mut all_lines = self.output_lines.clone();

        // 현재 타이핑 중인 텍스트가 있다면 추가
        if self.is_typing && !self.typing_text.is_empty() {
            let typing_display = format!("{}█", self.typing_text);
            all_lines.push(typing_display);
        }

        // 스크롤 오프셋 적용하여 표시할 라인들만 추출
        let start_idx = self.scroll_offset.min(all_lines.len());
        let end_idx = (start_idx + self.max_display_lines).min(all_lines.len());

        if start_idx < end_idx {
            all_lines[start_idx..end_idx].join("\n")
        } else {
            String::new()
        }
    }
    
    pub fn set_typing_speed_fast(&mut self){
        self.typing_speed = Duration::from_millis(10);
    }

    pub fn set_typing_speed_normal(&mut self){
        self.typing_speed = Duration::from_millis(30);
    }

    pub fn set_typing_speed_slow(&mut self){
        self.typing_speed = Duration::from_millis(80);
    }

    pub fn skip_typing(&mut self){
        if self.is_typing{
            self.output_lines.push(self.typing_target.clone());

            while let Some(text) =  self.typing_queue.pop_front(){
                self.output_lines.push(text);
            }

            self.typing_text.clear();
            self.typing_target.clear();
            self.typing_index = 0;
            self.is_typing = false;

            if !self.is_manually_scrolled{
                self.scroll_to_bottom();
            }
        }
    }

    pub fn get_total_lines(&self) -> usize {
        let mut total = self.output_lines.len();
        
        // 현재 타이핑 중인 텍스트가 있다면 +1
        if self.is_typing && !self.typing_text.is_empty() {
            total += 1;
        }
        
        total
    }


    fn get_visible_lines(&self) -> String {
        let start = self.scroll_offset;
        let end = (start + self.max_display_lines).min(self.output_lines.len());
        self.output_lines[start..end].join("\n")
    }

    pub fn scroll_up(&mut self) {
        if self.scroll_offset > 0 {
            self.scroll_offset -= 1;
            self.is_manually_scrolled = true;
        }
    }

    fn scroll_to_bottom(&mut self) {
        let total_lines = self.get_total_lines();
        if total_lines > self.max_display_lines {
            self.scroll_offset = total_lines - self.max_display_lines;
        } else {
            self.scroll_offset = 0;
        }
    }

    pub fn send_input(&mut self) {
        if !self.current_input.trim().is_empty() {
            let input = self.current_input.clone();
            
            self.input_history.push_back(input.clone());
            if self.input_history.len() > 20 {
                self.input_history.pop_front();
            }
            
            // 사용자 입력은 즉시 표시
            self.add_system_message(&format!("👤 {}", input));
            
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
        let chars: Vec<char> = self.current_input.chars().collect();
        let mut new_chars = chars;
        
        if self.cursor_position <= new_chars.len() {
            new_chars.insert(self.cursor_position, c);
            self.current_input = new_chars.into_iter().collect();
            self.cursor_position += 1; 
        }
    }

    pub fn handle_backspace(&mut self) {
        if self.cursor_position > 0 {
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
                .take(5)
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
        if self.is_python_running {
            self.user_status = "🎮 게임 진행 중 | 모험가 준비됨".to_string();
            self.equipment_status = "⚔️ 장비: 준비 완료 | 📦 인벤토리: 정상".to_string();
        } else {
            self.user_status = "⏸️ 게임 일시정지".to_string();
            self.equipment_status = "❌ 연결 끊김".to_string();
        }
    }
} 