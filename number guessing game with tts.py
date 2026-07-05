import random
import time
import json
import threading
from datetime import datetime
import os
import sys

# Import libraries with fallback handling
try:
    import pyttsx3
    TTS_AVAILABLE = True
except ImportError:
    TTS_AVAILABLE = False
    print("⚠️ pyttsx3 not installed. Run: pip install pyttsx3")

try:
    import pygame
    PYGAME_AVAILABLE = True
except ImportError:
    PYGAME_AVAILABLE = False
    print("⚠️ pygame not installed. Run: pip install pygame")

try:
    from colorama import init, Fore, Back, Style
    init()  # Initialize colorama
    COLORAMA_AVAILABLE = True
except ImportError:
    COLORAMA_AVAILABLE = False
    print("⚠️ colorama not installed. Run: pip install colorama")

try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False
    print("⚠️ speech_recognition not installed. Run: pip install SpeechRecognition")

try:
    import playsound
    PLAYSOUND_AVAILABLE = True
except ImportError:
    PLAYSOUND_AVAILABLE = False
    print("⚠️ playsound not installed. Run: pip install playsound")

class VoiceNumberGuessingGame:
    def __init__(self):
        self.stats = {
            'games_played': 0,
            'games_won': 0,
            'total_guesses': 0,
            'best_score': float('inf'),
            'win_streak': 0,
            'current_streak': 0,
            'voice_enabled': True,
            'speech_input_enabled': False,
            'sound_effects': True
        }
        
        # Initialize TTS engine
        if TTS_AVAILABLE:
            self.tts_engine = pyttsx3.init()
            self.setup_voice()
        
        # Initialize pygame for sound effects
        if PYGAME_AVAILABLE:
            pygame.mixer.init()
            self.create_sound_effects()
        
        # Initialize speech recognition
        if SPEECH_RECOGNITION_AVAILABLE:
            self.recognizer = sr.Recognizer()
            self.microphone = sr.Microphone()
        
        self.load_stats()
        
    def setup_voice(self):
        """Configure the TTS engine"""
        if not TTS_AVAILABLE:
            return
            
        voices = self.tts_engine.getProperty('voices')
        if voices:
            # Try to set a female voice if available
            for voice in voices:
                if 'female' in voice.name.lower() or 'zira' in voice.name.lower():
                    self.tts_engine.setProperty('voice', voice.id)
                    break
        
        # Set speech rate and volume
        self.tts_engine.setProperty('rate', 180)
        self.tts_engine.setProperty('volume', 0.9)
    
    def create_sound_effects(self):
        """Generate simple sound effects using pygame"""
        if not PYGAME_AVAILABLE:
            return
            
        # Create sound arrays for different effects
        sample_rate = 22050
        
        # Success sound (ascending notes)
        self.success_sound = self.generate_tone(440, 0.2, sample_rate)
        
        # Error sound (descending tone)
        self.error_sound = self.generate_tone(200, 0.3, sample_rate)
        
        # Close guess sound (bell-like)
        self.close_sound = self.generate_tone(800, 0.1, sample_rate)
    
    def generate_tone(self, frequency, duration, sample_rate):
        """Generate a simple sine wave tone"""
        if not PYGAME_AVAILABLE:
            return None
            
        import numpy as np
        frames = int(duration * sample_rate)
        arr = np.zeros((frames, 2))
        
        for i in range(frames):
            wave = np.sin(2 * np.pi * frequency * i / sample_rate)
            arr[i] = [wave, wave]
        
        arr = (arr * 32767).astype(np.int16)
        sound = pygame.sndarray.make_sound(arr)
        return sound
    
    def speak(self, text, wait=False):
        """Convert text to speech"""
        if not TTS_AVAILABLE or not self.stats['voice_enabled']:
            return
            
        def speak_thread():
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        
        if wait:
            speak_thread()
        else:
            threading.Thread(target=speak_thread, daemon=True).start()
    
    def play_sound(self, sound_type):
        """Play sound effects"""
        if not PYGAME_AVAILABLE or not self.stats['sound_effects']:
            return
            
        try:
            if sound_type == 'success' and hasattr(self, 'success_sound'):
                self.success_sound.play()
            elif sound_type == 'error' and hasattr(self, 'error_sound'):
                self.error_sound.play()
            elif sound_type == 'close' and hasattr(self, 'close_sound'):
                self.close_sound.play()
        except:
            pass
    
    def listen_for_speech(self):
        """Listen for speech input and convert to text"""
        if not SPEECH_RECOGNITION_AVAILABLE:
            return None
            
        try:
            print("🎤 Listening... (speak your guess)")
            self.speak("Please speak your guess")
            
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=3)
            
            print("🔄 Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"👂 Heard: {text}")
            
            # Extract number from speech
            import re
            numbers = re.findall(r'\d+', text)
            if numbers:
                return int(numbers[0])
            else:
                print("❌ No number detected in speech")
                return None
                
        except sr.WaitTimeoutError:
            print("⏰ No speech detected within timeout")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand the speech")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
    
    def colored_print(self, text, color='white'):
        """Print colored text if colorama is available"""
        if not COLORAMA_AVAILABLE:
            print(text)
            return
            
        colors = {
            'red': Fore.RED,
            'green': Fore.GREEN,
            'yellow': Fore.YELLOW,
            'blue': Fore.BLUE,
            'magenta': Fore.MAGENTA,
            'cyan': Fore.CYAN,
            'white': Fore.WHITE,
            'bright_green': Fore.LIGHTGREEN_EX,
            'bright_red': Fore.LIGHTRED_EX,
            'bright_yellow': Fore.LIGHTYELLOW_EX
        }
        
        color_code = colors.get(color, Fore.WHITE)
        print(f"{color_code}{text}{Style.RESET_ALL}")
    
    def animated_print(self, text, delay=0.03, color='white'):
        """Print text with typewriter effect"""
        for char in text:
            if COLORAMA_AVAILABLE:
                colors = {
                    'red': Fore.RED, 'green': Fore.GREEN, 'yellow': Fore.YELLOW,
                    'blue': Fore.BLUE, 'magenta': Fore.MAGENTA, 'cyan': Fore.CYAN,
                    'white': Fore.WHITE, 'bright_green': Fore.LIGHTGREEN_EX
                }
                color_code = colors.get(color, Fore.WHITE)
                print(f"{color_code}{char}{Style.RESET_ALL}", end='', flush=True)
            else:
                print(char, end='', flush=True)
            time.sleep(delay)
        print()
    
    def load_stats(self):
        """Load game statistics from file"""
        try:
            with open('voice_game_stats.json', 'r') as f:
                loaded_stats = json.load(f)
                self.stats.update(loaded_stats)
        except FileNotFoundError:
            pass
    
    def save_stats(self):
        """Save game statistics to file"""
        with open('voice_game_stats.json', 'w') as f:
            json.dump(self.stats, f, indent=2)
    
    def display_banner(self):
        """Display animated game banner"""
        os.system('cls' if os.name == 'nt' else 'clear')  # Clear screen
        
        banner = """
╔══════════════════════════════════════════════════════════╗
║           🎤 VOICE-ENABLED NUMBER GUESSING GAME 🎯        ║
╚══════════════════════════════════════════════════════════╝
"""
        self.animated_print(banner, delay=0.01, color='cyan')
        
        stats_text = f"""
📊 Games: {self.stats['games_played']} | 🏆 Win Rate: {self.get_win_rate():.1f}% | 🔥 Streak: {self.stats['current_streak']}
🎯 Best Score: {self.stats['best_score'] if self.stats['best_score'] != float('inf') else 'N/A'} | 🎙️ Voice: {'ON' if self.stats['voice_enabled'] else 'OFF'} | 🔊 Sounds: {'ON' if self.stats['sound_effects'] else 'OFF'}
"""
        self.colored_print(stats_text, 'yellow')
    
    def get_win_rate(self):
        """Calculate win rate percentage"""
        if self.stats['games_played'] == 0:
            return 0
        return (self.stats['games_won'] / self.stats['games_played']) * 100
    
    def get_difficulty(self):
        """Let player choose difficulty with voice announcement"""
        difficulty_text = """
🎮 Choose Your Challenge Level:
1. 👶 Beginner (1-30, 8 guesses)
2. 😊 Easy (1-50, 7 guesses) 
3. 🤔 Medium (1-100, 6 guesses)
4. 😤 Hard (1-200, 5 guesses)
5. 🔥 Expert (1-500, 4 guesses)
6. ⚙️ Custom Range
"""
        self.colored_print(difficulty_text, 'bright_yellow')
        self.speak("Choose your difficulty level")
        
        while True:
            try:
                choice = input("Enter choice (1-6): ")
                
                difficulties = {
                    '1': (30, 8, "Beginner"),
                    '2': (50, 7, "Easy"), 
                    '3': (100, 6, "Medium"),
                    '4': (200, 5, "Hard"),
                    '5': (500, 4, "Expert")
                }
                
                if choice in difficulties:
                    max_num, max_guesses, level = difficulties[choice]
                    self.speak(f"You selected {level} mode. Good luck!")
                    return max_num, max_guesses
                elif choice == '6':
                    max_num = int(input("Enter maximum number: "))
                    max_guesses = int(input("Enter maximum guesses: "))
                    self.speak(f"Custom game with numbers up to {max_num}")
                    return max_num, max_guesses
                else:
                    self.colored_print("❌ Invalid choice! Please enter 1-6.", 'red')
                    self.play_sound('error')
            except ValueError:
                self.colored_print("❌ Please enter a valid number!", 'red')
                self.play_sound('error')
    
    def give_hint(self, target, guess, attempt):
        """Provide animated hints with voice and sound effects"""
        diff = abs(target - guess)
        
        if diff == 0:
            hint = "🎉 PERFECT! You nailed it!"
            color = 'bright_green'
            self.speak("Perfect! You got it exactly right!")
            self.play_sound('success')
        elif diff <= 2:
            hint = "🔥 BURNING HOT! You're within 2 numbers!"
            color = 'bright_red'
            self.speak("Burning hot! You're so close!")
            self.play_sound('close')
        elif diff <= 5:
            hint = "♨️ VERY HOT! You're within 5 numbers!"
            color = 'red'
            self.speak("Very hot! Almost there!")
            self.play_sound('close')
        elif diff <= 10:
            hint = "🌡️ HOT! You're within 10 numbers!"
            color = 'yellow'
            self.speak("Hot! You're getting warmer!")
        elif diff <= 20:
            hint = "😊 WARM! You're within 20 numbers!"
            color = 'green'
            self.speak("Warm! Keep going!")
        elif diff <= 50:
            hint = "❄️ COOL! You're getting there!"
            color = 'blue'
            self.speak("Cool! You're on the right track!")
        else:
            hint = "🧊 ICE COLD! Way off target!"
            color = 'cyan'
            self.speak("Ice cold! Try a completely different range!")
            self.play_sound('error')
        
        self.animated_print(hint, delay=0.05, color=color)
        return hint
    
    def get_user_input(self):
        """Get user input via keyboard or speech"""
        if self.stats['speech_input_enabled'] and SPEECH_RECOGNITION_AVAILABLE:
            self.colored_print("🎤 Say your guess or type 'text' for keyboard input:", 'cyan')
            
            # Try speech first
            guess = self.listen_for_speech()
            if guess is not None:
                return guess
            
            # Fallback to text input
            self.colored_print("📝 Falling back to text input:", 'yellow')
        
        return int(input("Enter your guess: "))
    
    def play_round(self):
        """Play a single round with enhanced interactions"""
        max_number, max_guesses = self.get_difficulty()
        target = random.randint(1, max_number)
        guesses = []
        
        # Game start announcement
        start_msg = f"🎯 I'm thinking of a number between 1 and {max_number}!"
        self.animated_print(start_msg, color='bright_green')
        self.speak(f"I'm thinking of a number between 1 and {max_number}. You have {max_guesses} guesses.")
        
        time.sleep(1)
        start_time = time.time()
        
        for attempt in range(1, max_guesses + 1):
            print("\n" + "="*60)
            attempt_msg = f"🎯 ATTEMPT {attempt}/{max_guesses}"
            self.colored_print(attempt_msg, 'bright_yellow')
            
            # Show previous guesses with colors
            if guesses:
                guess_history = "📋 Previous guesses: " + " | ".join([
                    f"{'🔴' if abs(g - target) > 20 else '🟡' if abs(g - target) > 10 else '🟢'}{g}" 
                    for g in guesses
                ])
                self.colored_print(guess_history, 'magenta')
            
            try:
                guess = self.get_user_input()
                
                if guess in guesses:
                    self.colored_print("⚠️ You already tried that number!", 'yellow')
                    self.speak("You already guessed that number!")
                    self.play_sound('error')
                    continue
                
                guesses.append(guess)
                
                if guess == target:
                    # Victory celebration
                    end_time = time.time()
                    time_taken = round(end_time - start_time, 2)
                    
                    victory_msg = f"""
🎊🎉🎊🎉🎊🎉🎊🎉🎊🎉🎊🎉🎊🎉🎊
    🏆 INCREDIBLE! YOU WON! 🏆
🎊🎉🎊🎉🎊🎉🎊🎉🎊🎉🎊🎉🎊🎉🎊

✨ Number: {target}
⚡ Attempts: {attempt}
⏱️ Time: {time_taken} seconds
🎯 Accuracy: {((max_guesses - attempt + 1) / max_guesses * 100):.1f}%
"""
                    self.animated_print(victory_msg, delay=0.02, color='bright_green')
                    self.speak(f"Incredible! You guessed {target} in just {attempt} attempts! Amazing work!")
                    
                    # Victory sound sequence
                    for _ in range(3):
                        self.play_sound('success')
                        time.sleep(0.2)
                    
                    # Update stats
                    self.update_win_stats(attempt)
                    return True
                
                else:
                    # Wrong guess feedback
                    direction = "📈 HIGHER" if guess < target else "📉 LOWER"
                    direction_color = 'green' if guess < target else 'red'
                    
                    self.colored_print(f"❌ {guess} is too {'low' if guess < target else 'high'}! Go {direction}!", direction_color)
                    self.speak(f"{guess} is too {'low' if guess < target else 'high'}")
                    
                    # Give contextual hint
                    self.give_hint(target, guess, attempt)
                    
                    remaining = max_guesses - attempt
                    if remaining > 0:
                        remaining_msg = f"🔄 {remaining} guesses remaining"
                        self.colored_print(remaining_msg, 'cyan')
                        if remaining <= 2:
                            self.speak(f"Only {remaining} guesses left! Make them count!")
                    
                    time.sleep(0.5)  # Brief pause for dramatic effect
            
            except ValueError:
                self.colored_print("⚠️ Please enter a valid number!", 'red')
                self.play_sound('error')
                continue
        
        # Game over sequence
        game_over_msg = f"""
💥💥💥 GAME OVER! 💥💥💥
🎯 The number was: {target}
📋 Your guesses: {' → '.join(map(str, guesses))}
💪 Don't give up! Try again!
"""
        self.animated_print(game_over_msg, delay=0.03, color='red')
        self.speak(f"Game over! The number was {target}. Better luck next time!")
        
        # Update loss stats
        self.update_loss_stats(max_guesses)
        return False
    
    def update_win_stats(self, attempts):
        """Update statistics for a win"""
        self.stats['games_played'] += 1
        self.stats['games_won'] += 1
        self.stats['total_guesses'] += attempts
        self.stats['current_streak'] += 1
        
        if attempts < self.stats['best_score']:
            self.stats['best_score'] = attempts
            self.speak("New personal best score!")
        
        if self.stats['current_streak'] > self.stats['win_streak']:
            self.stats['win_streak'] = self.stats['current_streak']
    
    def update_loss_stats(self, max_guesses):
        """Update statistics for a loss"""
        self.stats['games_played'] += 1
        self.stats['total_guesses'] += max_guesses
        self.stats['current_streak'] = 0
    
    def settings_menu(self):
        """Interactive settings menu"""
        while True:
            self.colored_print("\n⚙️ GAME SETTINGS", 'bright_yellow')
            settings_text = f"""
1. 🎙️ Voice Announcements: {'ON' if self.stats['voice_enabled'] else 'OFF'}
2. 🎤 Speech Input: {'ON' if self.stats['speech_input_enabled'] else 'OFF'}
3. 🔊 Sound Effects: {'ON' if self.stats['sound_effects'] else 'OFF'}
4. 🎵 Test Voice
5. 🎤 Test Microphone
6. 🔙 Back to Main Menu
"""
            print(settings_text)
            
            choice = input("Enter choice (1-6): ")
            
            if choice == '1':
                self.stats['voice_enabled'] = not self.stats['voice_enabled']
                status = "enabled" if self.stats['voice_enabled'] else "disabled"
                self.colored_print(f"✅ Voice announcements {status}!", 'green')
                if self.stats['voice_enabled']:
                    self.speak("Voice announcements are now enabled!")
                    
            elif choice == '2':
                if SPEECH_RECOGNITION_AVAILABLE:
                    self.stats['speech_input_enabled'] = not self.stats['speech_input_enabled']
                    status = "enabled" if self.stats['speech_input_enabled'] else "disabled"
                    self.colored_print(f"✅ Speech input {status}!", 'green')
                    self.speak(f"Speech input is now {status}")
                else:
                    self.colored_print("❌ Speech recognition not available!", 'red')
                    
            elif choice == '3':
                self.stats['sound_effects'] = not self.stats['sound_effects']
                status = "enabled" if self.stats['sound_effects'] else "disabled"
                self.colored_print(f"✅ Sound effects {status}!", 'green')
                if self.stats['sound_effects']:
                    self.play_sound('success')
                    
            elif choice == '4':
                self.speak("This is a test of the voice system. How do I sound?")
                
            elif choice == '5':
                if SPEECH_RECOGNITION_AVAILABLE:
                    self.colored_print("🎤 Say something to test the microphone...", 'cyan')
                    result = self.listen_for_speech()
                    if result:
                        self.colored_print(f"✅ Microphone working! Heard number: {result}", 'green')
                    else:
                        self.colored_print("❌ Microphone test failed", 'red')
                else:
                    self.colored_print("❌ Speech recognition not available!", 'red')
                    
            elif choice == '6':
                break
            else:
                self.colored_print("❌ Invalid choice!", 'red')
                self.play_sound('error')
    
    def show_statistics(self):
        """Display enhanced statistics with voice"""
        stats_display = f"""
╔════════════════════════════════════════╗
║            📊 GAME STATISTICS          ║
╚════════════════════════════════════════╝

🎮 Games Played: {self.stats['games_played']}
🏆 Games Won: {self.stats['games_won']}
📈 Win Rate: {self.get_win_rate():.1f}%
🎯 Total Guesses: {self.stats['total_guesses']}
"""
        
        if self.stats['games_won'] > 0:
            avg_guesses = self.stats['total_guesses'] / self.stats['games_won']
            stats_display += f"""⚡ Average Guesses per Win: {avg_guesses:.1f}
🎯 Best Score: {self.stats['best_score']}
"""
        
        stats_display += f"""🔥 Current Win Streak: {self.stats['current_streak']}
🏅 Best Win Streak: {self.stats['win_streak']}

╔════════════════════════════════════════╗
"""
        
        self.animated_print(stats_display, delay=0.02, color='cyan')
        
        # Voice summary
        if self.stats['games_played'] > 0:
            summary = f"You've played {self.stats['games_played']} games with a {self.get_win_rate():.1f}% win rate"
            if self.stats['current_streak'] > 0:
                summary += f" and you're on a {self.stats['current_streak']} game winning streak!"
            self.speak(summary)
    
    def main_menu(self):
        """Enhanced main menu with voice navigation"""
        while True:
            self.display_banner()
            
            menu_text = """
🎮 MAIN MENU - Choose Your Adventure:

1. 🎯 Start New Game
2. 📊 View Statistics  
3. ⚙️ Settings
4. 📖 How to Play
5. 🔄 Reset All Data
6. 👋 Quit Game
"""
            self.colored_print(menu_text, 'bright_yellow')
            
            choice = input("Enter your choice (1-6): ")
            
            if choice == '1':
                self.speak("Starting a new game! Get ready!")
                won = self.play_round()
                
                if won:
                    self.colored_print("\n🌟 Excellent work! Ready for another challenge?", 'bright_green')
                else:
                    self.colored_print("\n💪 Great effort! Practice makes perfect!", 'yellow')
                
                input("\n⏸️ Press Enter to continue...")
                
            elif choice == '2':
                self.show_statistics()
                input("\n⏸️ Press Enter to continue...")
                
            elif choice == '3':
                self.settings_menu()
                
            elif choice == '4':
                self.show_help()
                input("\n⏸️ Press Enter to continue...")
                
            elif choice == '5':
                self.colored_print("⚠️ This will delete ALL your progress!", 'red')
                confirm = input("Type 'RESET' to confirm: ")
                if confirm == 'RESET':
                    self.reset_stats()
                    self.speak("All statistics have been reset!")
                    
            elif choice == '6':
                self.save_stats()
                goodbye_msg = "👋 Thanks for playing! Your progress has been saved. See you next time!"
                self.animated_print(goodbye_msg, color='bright_green')
                self.speak("Thanks for playing! See you next time!")
                break
                
            else:
                self.colored_print("❌ Invalid choice! Please enter 1-6.", 'red')
                self.play_sound('error')
    
    def show_help(self):
        """Display comprehensive help with voice"""
        help_text = """
╔══════════════════════════════════════════════════════════╗
║                    📖 HOW TO PLAY                        ║
╚══════════════════════════════════════════════════════════╝

🎯 OBJECTIVE: Guess the secret number in the fewest attempts!

🎮 AMAZING FEATURES:
• 🎙️ Voice announcements and hints
• 🎤 Speech recognition for hands-free play  
• 🔊 Sound effects for immersive experience
• 🌈 Colorful animated interface
• 📊 Detailed statistics tracking
• 🏆 Achievement system with streaks
• ⚙️ Customizable settings

💡 SMART HINT SYSTEM:
🔥 Burning Hot: Within 2 numbers - You're almost there!
♨️ Very Hot: Within 5 numbers - So close!
🌡️ Hot: Within 10 numbers - Getting warmer!
😊 Warm: Within 20 numbers - On the right track!
❄️ Cool: Within 50 numbers - Keep trying!
🧊 Ice Cold: Way off - Try a different range!

🎤 VOICE CONTROLS:
• Enable speech input in settings
• Simply speak your number guess
• Clear pronunciation works best
• Falls back to keyboard if needed

🎵 SOUND EFFECTS:
• Success sounds for correct guesses
• Error sounds for mistakes  
• Special sounds for close guesses
• Victory celebration sequences

╔══════════════════════════════════════════════════════════╗
"""
        self.animated_print(help_text, delay=0.01, color='bright_yellow')
        self.speak("This game features voice announcements, speech recognition, and sound effects for the ultimate guessing experience!")
    
    def reset_stats(self):
        """Reset all statistics"""
        self.stats = {
            'games_played': 0,
            'games_won': 0, 
            'total_guesses': 0,
            'best_score': float('inf'),
            'win_streak': 0,
            'current_streak': 0,
            'voice_enabled': True,
            'speech_input_enabled': False,
            'sound_effects': True
        }
        self.colored_print("✅ All statistics have been reset!", 'green')

def main():
    """Main function with enhanced error handling"""
    print("🚀 Initializing Voice-Enabled Number Guessing Game...")
    
    # Check for required libraries
    missing_libs = []
    if not TTS_AVAILABLE:
        missing_libs.append("pyttsx3")
    if not PYGAME_AVAILABLE:
        missing_libs.append("pygame") 
    if not COLORAMA_AVAILABLE:
        missing_libs.append("colorama")
    if not SPEECH_RECOGNITION_AVAILABLE:
        missing_libs.append("SpeechRecognition")
    
    if missing_libs:
        print(f"\n⚠️ Optional libraries missing: {', '.join(missing_libs)}")
        print("💡 Install them for the full experience:")
        print(f"   pip install {' '.join(missing_libs)}")
        print("\n🎮 Game will run with available features...\n")
        time.sleep(2)
    
    game = VoiceNumberGuessingGame()
    
    try:
        game.main_menu()
    except KeyboardInterrupt:
        print("\n\n🛑 Game interrupted by user")
        game.save_stats()
        game.speak("Game interrupted. Your progress has been saved!")
        print("💾 Progress saved. Thanks for playing!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        game.save_stats()
        print("💾 Progress saved despite the error.")

if __name__ == "__main__":
    main()