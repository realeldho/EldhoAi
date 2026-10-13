import os
from tkinter import filedialog, messagebox

from file_support import (
    choose_files,
    read_text_file,
    build_message_with_attachments,
    MAX_ATTACHMENTS,
)
import re
import threading
import customtkinter as ctk

from audio_support import VoiceRecorder, speak_text, stop_speaking, transcribe_audio_file

from brain import (
    stream_eldho_ai,
    start_new_chat,
    switch_chat,
    get_saved_chats,
    get_active_chat,
    rename_chat,
    remove_chat,
    prepare_regenerate,
    regenerate_response,
    edit_chat_message,
    stream_edited_response,
    stop_generation
)

from app_settings import load_settings, save_settings

class EldhoAiApp(ctk.CTk):

    def __init__(self):
        super().__init__()

        # ====================================================
        # WINDOW
        # ====================================================

        self.title("EldhoAi")

        self.geometry(
            "1150x750"
        )

        self.minsize(
            900,
            600
        )

        # ====================================================
        # LOAD SAVED APPEARANCE SETTINGS
        # ====================================================

        initial_settings = load_settings()

        ctk.set_appearance_mode(
            initial_settings.get("appearance", "dark")
        )

        ctk.set_widget_scaling(
            initial_settings.get("ui_scale", 1.0)
        )


        # ====================================================
        # COLORS
        # ====================================================

        self.bg_color = "#101114"

        self.sidebar_color = "#17191d"

        self.chat_color = "#101114"

        self.ai_bubble_color = "#1d2025"

        self.user_bubble_color = "#2563eb"

        self.input_color = "#202329"

        self.active_chat_color = "#24272d"

        self.active_chat_hover = "#2c3037"


        self.configure(
            fg_color=self.bg_color
        )


        # ====================================================
        # GENERATION STATE
        # ====================================================

        self.is_generating = False

        # Files currently selected for the next message.
        self.selected_attachments = []

        # Voice interaction state.
        self.voice_recorder = VoiceRecorder()
        self.is_recording_voice = False
        self.is_transcribing_voice = False

        self.streaming_row = None

        self.streaming_bubble = None

        self.streaming_content = None


        # ====================================================
        # HISTORY
        # ====================================================

        self.history_buttons = []


        # ====================================================
        # MAIN GRID
        # ====================================================

        self.grid_columnconfigure(
            1,
            weight=1
        )

        self.grid_rowconfigure(
            0,
            weight=1
        )


        # ====================================================
        # SIDEBAR
        # ====================================================

        self.sidebar = ctk.CTkFrame(
            self,
            width=245,
            corner_radius=0,
            fg_color=self.sidebar_color
        )

        self.sidebar.grid(
            row=0,
            column=0,
            sticky="nsew"
        )

        self.sidebar.grid_propagate(
            False
        )


        # ====================================================
        # LOGO
        # ====================================================

        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="✦ EldhoAi",
            font=ctk.CTkFont(
                size=27,
                weight="bold"
            )
        )

        self.logo.pack(
            padx=25,
            pady=(30, 25),
            anchor="w"
        )


        # ====================================================
        # NEW CHAT
        # ====================================================

        self.new_chat_button = ctk.CTkButton(
            self.sidebar,
            text="＋  New Chat",
            height=46,
            corner_radius=12,
            font=ctk.CTkFont(
                size=14,
                weight="bold"
            ),
            command=self.new_chat
        )

        self.new_chat_button.pack(
            padx=20,
            pady=5,
            fill="x"
        )


        # ====================================================
        # HISTORY LABEL
        # ====================================================

        self.history_label = ctk.CTkLabel(
            self.sidebar,
            text="CHAT HISTORY",
            font=ctk.CTkFont(
                size=11,
                weight="bold"
            ),
            text_color="#858993"
        )

        self.history_label.pack(
            padx=22,
            pady=(35, 12),
            anchor="w"
        )


        # ====================================================
        # HISTORY LIST
        # ====================================================

        self.history_list = ctk.CTkScrollableFrame(
            self.sidebar,
            fg_color="transparent"
        )

        self.history_list.pack(
            fill="both",
            expand=True,
            padx=4
        )


        # ====================================================
        # SETTINGS
        # ====================================================

        self.settings_button = ctk.CTkButton(
            self.sidebar,
            text="⚙  Settings",
            fg_color="transparent",
            hover_color="#24272d",
            anchor="w",
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(
                size=13
            ),
            command=self.open_settings
        )

        self.settings_button.pack(
            side="bottom",
            padx=12,
            pady=18,
            fill="x"
        )


        # ====================================================
        # EXPORT ACTIVE CHAT
        # ====================================================

        self.export_chat_button = ctk.CTkButton(
            self.sidebar,
            text="⇩  Export Chat",
            fg_color="transparent",
            hover_color="#24272d",
            anchor="w",
            height=42,
            corner_radius=8,
            font=ctk.CTkFont(size=13),
            command=self.export_chat
        )

        # Packed after Settings so this button appears just above it.
        self.export_chat_button.pack(
            side="bottom",
            padx=12,
            pady=(0, 4),
            fill="x"
        )


        # ====================================================
        # MAIN CHAT AREA
        # ====================================================

        self.chat_area = ctk.CTkFrame(
            self,
            corner_radius=0,
            fg_color=self.chat_color
        )

        self.chat_area.grid(
            row=0,
            column=1,
            sticky="nsew"
        )

        self.chat_area.grid_columnconfigure(
            0,
            weight=1
        )

        self.chat_area.grid_rowconfigure(
            1,
            weight=1
        )


        # ====================================================
        # TOP BAR
        # ====================================================

        self.top_bar = ctk.CTkFrame(
            self.chat_area,
            height=75,
            corner_radius=0,
            fg_color=self.chat_color
        )

        self.top_bar.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=28,
            pady=(15, 5)
        )


        self.title_label = ctk.CTkLabel(
            self.top_bar,
            text="EldhoAi",
            font=ctk.CTkFont(
                size=24,
                weight="bold"
            )
        )

        self.title_label.pack(
            anchor="w"
        )


        self.status_label = ctk.CTkLabel(
            self.top_bar,
            text="●  Online",
            text_color="#4ade80",
            font=ctk.CTkFont(
                size=13
            )
        )

        self.status_label.pack(
            anchor="w",
            pady=(2, 0)
        )


        # ====================================================
        # MESSAGE AREA
        # ====================================================

        self.messages = ctk.CTkScrollableFrame(
            self.chat_area,
            fg_color=self.chat_color,
            corner_radius=0
        )

        self.messages.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15,
            pady=5
        )


        # ====================================================
        # WELCOME
        # ====================================================

        self.create_welcome_screen()


        # ====================================================
        # INPUT AREA
        # ====================================================

        self.input_outer = ctk.CTkFrame(
            self.chat_area,
            fg_color=self.chat_color
        )

        self.input_outer.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=25,
            pady=(5, 22)
        )

        self.input_outer.grid_columnconfigure(
            0,
            weight=1
        )


        self.input_frame = ctk.CTkFrame(
            self.input_outer,
            height=58,
            corner_radius=17,
            fg_color=self.input_color,
            border_width=1,
            border_color="#343840"
        )

        self.input_frame.grid(
            row=0,
            column=0,
            sticky="ew"
        )

        # ====================================================
        # ATTACHMENT STATUS AREA
        # ====================================================

        self.attachment_info_frame = ctk.CTkFrame(
            self.input_outer,
            fg_color="transparent"
        )

        self.attachment_info_frame.grid(
            row=1,
            column=0,
            sticky="ew",
            padx=8,
            pady=(4, 0)
        )

        self.attachments_label = ctk.CTkLabel(
            self.attachment_info_frame,
            text="",
            text_color="#9296a0",
            font=ctk.CTkFont(size=11),
            anchor="w"
        )

        self.attachments_label.pack(
            side="left",
            fill="x",
            expand=True
        )

        self.clear_attachments_button = ctk.CTkButton(
            self.attachment_info_frame,
            text="Clear",
            width=55,
            height=25,
            corner_radius=7,
            fg_color="transparent",
            hover_color="#343840",
            command=self.clear_selected_attachments
        )

        self.clear_attachments_button.pack_forget()

        self.input_frame.grid_columnconfigure(
            0,
            weight=1
        )


        # ====================================================
        # INPUT
        # ====================================================

        # Multiline composer: Enter sends when that setting is enabled;
        # Shift+Enter inserts a newline instead.
        self.message_entry = ctk.CTkTextbox(
            self.input_frame,
            height=44,
            corner_radius=17,
            border_width=0,
            fg_color="transparent",
            font=ctk.CTkFont(size=15),
            wrap="word",
            activate_scrollbars=False
        )

        self.message_entry.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(18, 8),
            pady=3
        )

        self.message_entry.bind(
            "<Return>",
            self.send_message
        )
        self.message_entry.bind(
            "<KeyRelease>",
            self.update_input_placeholder
        )

        # CTkTextbox has no built-in placeholder, so use a label over it.
        self.message_placeholder = ctk.CTkLabel(
            self.input_frame,
            text="Message EldhoAi...",
            text_color="#8a8f98",
            fg_color="transparent",
            font=ctk.CTkFont(size=15),
            anchor="w"
        )
        self.message_placeholder.place(
            x=18,
            rely=0.5,
            anchor="w"
        )
        # The placeholder sits above the textbox, so explicitly route
        # clicks on it to the actual internal text widget. Calling
        # focus_set() on the CTkTextbox wrapper may not focus its editor.
        self.message_placeholder.bind(
            "<Button-1>",
            self.focus_message_input
        )
        self.message_entry._textbox.bind(
            "<FocusOut>",
            self.update_input_placeholder,
            add="+"
        )


        # ====================================================
        # SEND / STOP BUTTON
        # ====================================================

        # ====================================================
        # ATTACH FILE BUTTON
        # ====================================================

        self.attach_button = ctk.CTkButton(
            self.input_frame,
            text="📎",
            width=42,
            height=44,
            corner_radius=12,
            fg_color="transparent",
            hover_color="#343840",
            font=ctk.CTkFont(size=19),
            command=self.attach_files
        )

        self.attach_button.grid(
            row=0,
            column=1,
            padx=2
        )

        self.voice_button = ctk.CTkButton(
            self.input_frame,
            text="🎙️",
            width=42,
            height=44,
            corner_radius=12,
            fg_color="transparent",
            hover_color="#343840",
            font=ctk.CTkFont(size=18),
            command=self.toggle_voice_input
        )
        self.voice_button.grid(
            row=0,
            column=2,
            padx=2
        )

        self.stop_speech_button = ctk.CTkButton(
            self.input_frame,
            text="🔇",
            width=42,
            height=44,
            corner_radius=12,
            fg_color="transparent",
            hover_color="#343840",
            font=ctk.CTkFont(size=17),
            command=self.stop_voice_output
        )
        self.stop_speech_button.grid(
            row=0,
            column=3,
            padx=2
        )

        self.send_button = ctk.CTkButton(
            self.input_frame,
            text="➤",
            width=48,
            height=46,
            corner_radius=13,
            font=ctk.CTkFont(
                size=21,
                weight="bold"
            ),
            command=self.send_message
        )

        self.send_button.grid(
            row=0,
            column=4,
            padx=6
        )


        # ====================================================
        # LOAD HISTORY
        # ====================================================

        self.refresh_history()


        # ====================================================
        # FOCUS
        # ====================================================

        self.message_entry._textbox.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.close_app)


    # ========================================================
    # VOICE INPUT / OUTPUT
    # ========================================================

    def toggle_voice_input(self):
        """Start microphone recording, or stop and transcribe it."""
        if self.is_transcribing_voice:
            return

        if self.is_recording_voice:
            self.is_recording_voice = False
            self.is_transcribing_voice = True
            self.voice_button.configure(text="…", state="disabled")
            self.status_label.configure(
                text="●  Transcribing voice…",
                text_color="#facc15"
            )
            try:
                audio_path = self.voice_recorder.stop()
            except Exception as error:
                self.is_transcribing_voice = False
                self.voice_button.configure(text="🎙️", state="normal")
                self.status_label.configure(text="●  Online", text_color="#4ade80")
                messagebox.showerror("Voice input failed", str(error), parent=self)
                return

            threading.Thread(
                target=self._transcribe_voice_worker,
                args=(audio_path,),
                daemon=True
            ).start()
            return

        if self.is_generating:
            messagebox.showinfo(
                "Voice input",
                "Wait for EldhoAi to finish its current response before recording.",
                parent=self
            )
            return

        try:
            self.voice_recorder.start()
        except Exception as error:
            messagebox.showerror("Microphone unavailable", str(error), parent=self)
            return

        self.is_recording_voice = True
        self.voice_button.configure(
            text="■",
            fg_color="#9f3030",
            hover_color="#b83b3b",
            state="normal"
        )
        self.status_label.configure(
            text="●  Listening — click ■ when finished",
            text_color="#ef4444"
        )

    def _transcribe_voice_worker(self, audio_path):
        transcript = None
        error_text = None
        try:
            transcript = transcribe_audio_file(audio_path)
        except Exception as error:
            error_text = str(error)
        finally:
            try:
                os.remove(audio_path)
            except OSError:
                pass

        try:
            self.after(0, self._finish_voice_transcription, transcript, error_text)
        except Exception:
            pass

    def _finish_voice_transcription(self, transcript, error_text):
        self.is_transcribing_voice = False
        self.voice_button.configure(
            text="🎙️",
            fg_color="transparent",
            hover_color="#343840",
            state="normal"
        )

        if error_text:
            self.status_label.configure(text="●  Online", text_color="#4ade80")
            messagebox.showerror("Voice transcription failed", error_text, parent=self)
            return

        if not transcript or not transcript.strip():
            self.status_label.configure(text="●  Online", text_color="#4ade80")
            messagebox.showinfo(
                "No speech detected",
                "EldhoAi couldn't detect speech. Try recording again.",
                parent=self
            )
            return

        self.message_entry.configure(state="normal")
        self.message_entry.insert("insert", transcript.strip())
        self.update_input_placeholder()
        self.message_entry._textbox.focus_set()
        self.status_label.configure(
            text="●  Voice transcribed — review before sending",
            text_color="#60a5fa"
        )
        self.after(2500, lambda: self.status_label.configure(
            text="●  Online", text_color="#4ade80"
        ))

    def stop_voice_output(self):
        """Stop any response currently being read aloud."""
        stop_speaking()
        self.status_label.configure(
            text="●  Speech stopped",
            text_color="#60a5fa"
        )
        self.after(1500, lambda: self.status_label.configure(
            text="●  Online", text_color="#4ade80"
        ))

    def close_app(self):
        """Release microphone and speech resources before closing."""
        try:
            self.voice_recorder.cancel()
        except Exception:
            pass
        try:
            stop_speaking()
        except Exception:
            pass
        self.destroy()


    # ========================================================
    # WELCOME SCREEN
    # ========================================================

    def create_welcome_screen(self):

        self.welcome_frame = ctk.CTkFrame(
            self.messages,
            fg_color="transparent"
        )

        self.welcome_frame.pack(
            pady=160
        )


        self.welcome_icon = ctk.CTkLabel(
            self.welcome_frame,
            text="✦",
            font=ctk.CTkFont(
                size=45
            )
        )

        self.welcome_icon.pack()


        self.welcome_title = ctk.CTkLabel(
            self.welcome_frame,
            text="Welcome to EldhoAi",
            font=ctk.CTkFont(
                size=30,
                weight="bold"
            )
        )

        self.welcome_title.pack(
            pady=(10, 5)
        )


        self.welcome_subtitle = ctk.CTkLabel(
            self.welcome_frame,
            text="Your AI assistant is ready. Ask me anything.",
            font=ctk.CTkFont(
                size=15
            ),
            text_color="#9699a3"
        )

        self.welcome_subtitle.pack()

    # ========================================================
    # ATTACH FILES
    # ========================================================

    def attach_files(self):

        if self.is_generating:
            return

        paths = choose_files(self)

        if not paths:
            return

        errors = []

        existing_paths = {
            item["path"]
            for item in self.selected_attachments
        }

        for path in paths:

            # Prevent duplicates.

            absolute_path = os.path.abspath(path)

            if absolute_path in existing_paths:
                continue

            # Enforce the total attachment limit.

            if len(self.selected_attachments) >= MAX_ATTACHMENTS:
                errors.append(
                    f"Maximum of {MAX_ATTACHMENTS} files per message."
                )

                break

            try:

                attachment = read_text_file(
                    absolute_path
                )

                self.selected_attachments.append(
                    attachment
                )

                existing_paths.add(
                    absolute_path
                )

            except ValueError as error:

                errors.append(
                    str(error)
                )

        self.update_attachment_display()

        if errors:
            messagebox.showwarning(
                "Some files were not attached",
                "\n\n".join(errors),
                parent=self
            )

    # ========================================================
    # UPDATE ATTACHMENT DISPLAY
    # ========================================================

    def update_attachment_display(self):

        if not self.selected_attachments:
            self.attachments_label.configure(
                text=""
            )

            self.clear_attachments_button.pack_forget()

            return

        filenames = [
            item["name"]
            for item in self.selected_attachments
        ]

        text = (
                f"📎 {len(filenames)} attached: "
                + ", ".join(filenames)
        )

        if len(text) > 85:
            text = text[:82] + "..."

        self.attachments_label.configure(
            text=text
        )

        if not self.clear_attachments_button.winfo_manager():
            self.clear_attachments_button.pack(
                side="right",
                padx=(5, 0)
            )

    # ========================================================
    # CLEAR ATTACHMENTS
    # ========================================================

    def clear_selected_attachments(self):

        self.selected_attachments.clear()

        self.update_attachment_display()
    # ========================================================
    # SEND
    # ========================================================

    # ========================================================
    # INPUT PLACEHOLDER
    # ========================================================

    def focus_message_input(self, event=None):
        """Focus the real text editor when the placeholder is clicked."""
        self.message_placeholder.place_forget()
        editor = getattr(self.message_entry, "_textbox", None)
        if editor is not None:
            editor.focus_set()
            # A click on the placeholder has no meaningful text-widget
            # coordinates, so place the insertion cursor at the end.
            editor.mark_set("insert", "end-1c")
        else:
            self.message_entry.focus_set()
        return "break"

    def update_input_placeholder(self, event=None):
        """Show the composer placeholder only when it is empty."""
        try:
            text = self.message_entry.get("1.0", "end-1c")
        except Exception:
            return

        if text:
            self.message_placeholder.place_forget()
        else:
            if not self.message_placeholder.winfo_manager():
                self.message_placeholder.place(
                    x=18,
                    rely=0.5,
                    anchor="w"
                )

    # ========================================================
    # SEND MESSAGE
    # ========================================================

    def send_message(self, event=None):
        # Shift+Enter should fall through to CTkTextbox's default
        # binding, which inserts a newline instead of sending.
        if event is not None and (getattr(event, "state", 0) & 0x0001):
            return None

        # When Enter-to-send is disabled, allow the textbox's normal
        # Return binding to insert a newline.
        if event is not None:
            try:
                if not load_settings().get("enter_to_send", True):
                    return None
            except Exception:
                # If settings cannot be read, keep the default send
                # behavior rather than breaking keyboard input.
                pass

        if self.is_generating:
            return "break" if event is not None else None

        message = self.message_entry.get("1.0", "end-1c").strip()

        attachments = list(
            self.selected_attachments
        )

        # Allow attachments without a written question.

        if not message and not attachments:
            return "break" if event is not None else None

        # --------------------------------------------------------
        # BUILD AI PROMPT
        # --------------------------------------------------------

        if attachments:

            model_prompt = build_message_with_attachments(
                message,
                attachments
            )

        else:

            model_prompt = None

        attachment_names = [
            item["name"]
            for item in attachments
        ]

        image_attachments = [
            {
                "name": item["name"],
                "path": item.get("image_path"),
                "mime_type": item.get("mime_type"),
            }
            for item in attachments
            if item.get("is_image")
        ]

        # --------------------------------------------------------
        # BUILD VISIBLE MESSAGE
        # --------------------------------------------------------

        display_message = (
                message
                or "Please examine the attached file contents."
        )

        if attachment_names:
            display_message += (
                    "\n\n📎 Attached: "
                    + ", ".join(attachment_names)
            )

        # --------------------------------------------------------
        # REMOVE WELCOME SCREEN
        # --------------------------------------------------------

        if (
                hasattr(self, "welcome_frame")
                and self.welcome_frame.winfo_exists()
        ):
            self.welcome_frame.destroy()

        # --------------------------------------------------------
        # CLEAR INPUT
        # --------------------------------------------------------

        self.message_entry.delete(
            "1.0",
            "end"
        )
        self.update_input_placeholder()

        # --------------------------------------------------------
        # DISPLAY USER MESSAGE
        # --------------------------------------------------------

        self.add_message(
            display_message,
            "You",
            is_user=True,
            message_index=None
        )

        # --------------------------------------------------------
        # CLEAR SELECTED FILES FROM INPUT
        # --------------------------------------------------------

        self.clear_selected_attachments()

        # --------------------------------------------------------
        # START AI
        # --------------------------------------------------------

        self.start_generation(
            lambda: stream_eldho_ai(
                message,
                model_prompt=model_prompt,
                attachment_names=attachment_names,
                image_attachments=image_attachments
            )
        )

        return "break" if event is not None else None


    # ========================================================
    # START GENERATION
    # ========================================================

    def start_generation(
        self,
        stream_function
    ):

        self.is_generating = True


        self.message_entry.configure(
            state="disabled"
        )

        self.new_chat_button.configure(
            state="disabled"
        )


        # Change send button to STOP

        self.send_button.configure(
            text="■",
            command=self.stop_current_generation
        )


        self.status_label.configure(
            text="●  Thinking...",
            text_color="#facc15"
        )


        thread = threading.Thread(
            target=self.run_generation,
            args=(stream_function,),
            daemon=True
        )

        thread.start()


    # ========================================================
    # RUN GENERATION
    # ========================================================

    def run_generation(
        self,
        stream_function
    ):

        # The streaming widget redraws the supplied text, so pass the
        # cumulative response rather than only the latest chunk.
        full_response = ""

        try:

            for chunk in stream_function():

                full_response += chunk

                self.after(
                    0,
                    lambda text=full_response:
                        self.update_streaming_message(
                            text
                        )
                )


        except Exception as error:

            error_text = (
                "⚠️ **EldhoAi encountered an unexpected error.**\n\n"
                f"{error}"
            )

            full_response = (
                full_response + "\n\n" + error_text
                if full_response
                else error_text
            )

            self.after(
                0,
                lambda text=full_response:
                    self.update_streaming_message(
                        text
                    )
            )


        finally:

            self.after(
                0,
                self.finish_streaming_message
            )


    # ========================================================
    # STOP
    # ========================================================

    def stop_current_generation(self):

        if not self.is_generating:

            return


        stop_generation()


        self.status_label.configure(
            text="●  Stopping...",
            text_color="#facc15"
        )


    # ========================================================
    # STREAMING MESSAGE
    # ========================================================

    def update_streaming_message(
        self,
        text
    ):

        # ----------------------------------------------------
        # Create bubble
        # ----------------------------------------------------

        if self.streaming_row is None:

            self.streaming_row = ctk.CTkFrame(
                self.messages,
                fg_color="transparent"
            )

            self.streaming_row.pack(
                fill="x",
                padx=10,
                pady=6
            )


            self.streaming_bubble = ctk.CTkFrame(
                self.streaming_row,
                fg_color=self.ai_bubble_color,
                corner_radius=18
            )

            self.streaming_bubble.pack(
                side="left",
                anchor="w"
            )


            sender = ctk.CTkLabel(
                self.streaming_bubble,
                text="✦  EldhoAi",
                font=ctk.CTkFont(
                    size=12,
                    weight="bold"
                ),
                text_color="#ffffff"
            )

            sender.pack(
                anchor="w",
                padx=17,
                pady=(11, 4)
            )


            self.streaming_content = ctk.CTkFrame(
                self.streaming_bubble,
                fg_color="transparent"
            )

            self.streaming_content.pack(
                padx=17,
                pady=(0, 13),
                fill="x"
            )


        # ----------------------------------------------------
        # Clear previous render
        # ----------------------------------------------------

        for widget in self.streaming_content.winfo_children():

            widget.destroy()


        # ----------------------------------------------------
        # Render
        # ----------------------------------------------------

        self.insert_markdown(
            self.streaming_content,
            text,
            False
        )


        self.after(
            10,
            self.scroll_to_bottom
        )


    # ========================================================
    # FINISH STREAMING
    # ========================================================

    def finish_streaming_message(self):

        self.streaming_row = None

        self.streaming_bubble = None

        self.streaming_content = None


        self.is_generating = False


        # ----------------------------------------------------
        # Restore controls
        # ----------------------------------------------------

        self.message_entry.configure(
            state="normal"
        )

        self.new_chat_button.configure(
            state="normal"
        )


        # ----------------------------------------------------
        # Restore send button
        # ----------------------------------------------------

        self.send_button.configure(
            text="➤",
            command=self.send_message
        )


        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        self.status_label.configure(
            text="●  Online",
            text_color="#4ade80"
        )


        # ----------------------------------------------------
        # Reload active chat
        # ----------------------------------------------------

        active_chat = get_active_chat()


        if active_chat:

            self.load_chat_into_gui(
                active_chat
            )

        else:

            self.refresh_history()


        # Optionally read the latest AI reply aloud. Speech synthesis runs
        # on a background thread so it never blocks the chat interface.
        try:
            if (
                active_chat
                and load_settings().get("voice_replies", False)
                and active_chat.get("messages")
                and active_chat["messages"][-1].get("role") == "assistant"
            ):
                speak_text(active_chat["messages"][-1].get("content", ""))
        except Exception as error:
            print(f"EldhoAi could not start voice output: {error}")

        self.message_entry._textbox.focus_set()

        self.scroll_to_bottom()


    # ========================================================
    # ADD MESSAGE
    # ========================================================

    def add_message(
        self,
        message,
        sender,
        is_user=False,
        message_index=None
    ):

        row = ctk.CTkFrame(
            self.messages,
            fg_color="transparent"
        )

        row.pack(
            fill="x",
            padx=10,
            pady=6
        )


        bubble = ctk.CTkFrame(
            row,
            fg_color=(
                self.user_bubble_color
                if is_user
                else self.ai_bubble_color
            ),
            corner_radius=18
        )

        bubble.pack(
            side="right"
            if is_user
            else "left",
            anchor="e"
            if is_user
            else "w"
        )


        # ====================================================
        # SENDER
        # ====================================================

        sender_label = ctk.CTkLabel(
            bubble,
            text=(
                "👤  "
                if is_user
                else "✦  "
            ) + sender,
            font=ctk.CTkFont(
                size=12,
                weight="bold"
            ),
            text_color="#ffffff"
        )

        sender_label.pack(
            anchor="w",
            padx=17,
            pady=(11, 4)
        )


        # ====================================================
        # CONTENT
        # ====================================================

        content_frame = ctk.CTkFrame(
            bubble,
            fg_color="transparent"
        )

        content_frame.pack(
            padx=17,
            pady=(0, 5),
            fill="x"
        )


        self.insert_markdown(
            content_frame,
            message,
            is_user
        )


        # ====================================================
        # MESSAGE ACTIONS
        # ====================================================

        action_frame = ctk.CTkFrame(
            bubble,
            fg_color="transparent"
        )

        action_frame.pack(
            anchor="w",
            padx=12,
            pady=(2, 8)
        )


        # ----------------------------------------------------
        # COPY
        # ----------------------------------------------------

        copy_button = ctk.CTkButton(
            action_frame,
            text="Copy",
            width=50,
            height=26,
            corner_radius=7,
            fg_color="transparent",
            hover_color="#343840",
            font=ctk.CTkFont(
                size=11
            ),
            command=lambda text=message:
                self.copy_message(
                    text
                )
        )

        copy_button.pack(
            side="left",
            padx=2
        )


        # ----------------------------------------------------
        # USER: EDIT
        # ----------------------------------------------------

        if (
            is_user
            and message_index is not None
        ):

            edit_button = ctk.CTkButton(
                action_frame,
                text="Edit",
                width=46,
                height=26,
                corner_radius=7,
                fg_color="transparent",
                hover_color="#343840",
                font=ctk.CTkFont(
                    size=11
                ),
                command=lambda index=message_index:
                    self.open_edit_dialog(
                        index
                    )
            )

            edit_button.pack(
                side="left",
                padx=2
            )


        # ----------------------------------------------------
        # AI: REGENERATE
        # ----------------------------------------------------

        if (
            not is_user
            and message_index is not None
            and self.is_latest_message(
                message_index
            )
        ):

            regenerate_button = ctk.CTkButton(
                action_frame,
                text="Regenerate",
                width=80,
                height=26,
                corner_radius=7,
                fg_color="transparent",
                hover_color="#343840",
                font=ctk.CTkFont(
                    size=11
                ),
                command=self.regenerate_latest
            )

            regenerate_button.pack(
                side="left",
                padx=2
            )


    # ========================================================
    # CHECK LATEST MESSAGE
    # ========================================================

    def is_latest_message(
        self,
        message_index
    ):

        active_chat = get_active_chat()

        if not active_chat:

            return False


        chat_messages = active_chat.get(
            "messages",
            []
        )


        return (
            len(chat_messages) > 0
            and message_index == len(
                chat_messages
            ) - 1
        )


    # ========================================================
    # COPY MESSAGE
    # ========================================================

    def copy_message(
        self,
        text
    ):

        if self.is_generating:

            return


        try:

            self.clipboard_clear()

            self.clipboard_append(
                text
            )

            self.update()


            old_text = self.status_label.cget(
                "text"
            )

            old_color = self.status_label.cget(
                "text_color"
            )


            self.status_label.configure(
                text="●  Copied!",
                text_color="#60a5fa"
            )


            self.after(
                1200,
                lambda:
                    self.restore_status(
                        old_text,
                        old_color
                    )
            )


        except Exception:

            pass


    # ========================================================
    # RESTORE STATUS
    # ========================================================

    def restore_status(
        self,
        old_text,
        old_color
    ):

        if self.is_generating:

            return


        self.status_label.configure(
            text=old_text,
            text_color=old_color
        )


    # ========================================================
    # EDIT DIALOG
    # ========================================================

    def open_edit_dialog(
        self,
        message_index
    ):

        if self.is_generating:

            return


        active_chat = get_active_chat()

        if not active_chat:

            return


        chat_messages = active_chat.get(
            "messages",
            []
        )


        if (
            message_index < 0
            or message_index >= len(
                chat_messages
            )
        ):

            return


        original_message = chat_messages[
            message_index
        ]


        if original_message.get(
            "role"
        ) != "user":

            return


        dialog = ctk.CTkToplevel(
            self
        )

        dialog.title(
            "Edit Message"
        )

        dialog.geometry(
            "520x330"
        )

        dialog.resizable(
            False,
            False
        )

        dialog.transient(
            self
        )

        dialog.grab_set()


        # ====================================================
        # TITLE
        # ====================================================

        title = ctk.CTkLabel(
            dialog,
            text="✏  Edit Message",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        title.pack(
            pady=(25, 15)
        )


        # ====================================================
        # TEXTBOX
        # ====================================================

        textbox = ctk.CTkTextbox(
            dialog,
            height=150,
            corner_radius=10,
            font=ctk.CTkFont(
                size=14
            )
        )

        textbox.pack(
            padx=25,
            fill="x"
        )


        textbox.insert(
            "1.0",
            original_message.get(
                "content",
                ""
            )
        )

        textbox.focus()


        # ====================================================
        # SAVE
        # ====================================================

        def save_edit():

            new_text = textbox.get(
                "1.0",
                "end"
            ).strip()


            if not new_text:

                return


            success = edit_chat_message(
                message_index,
                new_text
            )


            if not success:

                return


            dialog.destroy()


            # Show modified conversation

            active_chat = get_active_chat()

            if active_chat:

                self.load_chat_into_gui(
                    active_chat
                )


            # Generate new answer

            self.start_generation(
                stream_edited_response
            )


        save_button = ctk.CTkButton(
            dialog,
            text="Save & Regenerate",
            height=42,
            corner_radius=10,
            command=save_edit
        )

        save_button.pack(
            padx=25,
            pady=18,
            fill="x"
        )


        textbox.bind(
            "<Control-Return>",
            lambda event:
                save_edit()
        )


    # ========================================================
    # REGENERATE
    # ========================================================

    def regenerate_latest(self):

        if self.is_generating:

            return


        success = prepare_regenerate()


        if not success:

            return


        active_chat = get_active_chat()


        if not active_chat:

            return


        # Remove old answer visually

        self.load_chat_into_gui(
            active_chat
        )


        # Generate again

        self.start_generation(
            regenerate_response
        )


    # ========================================================
    # OPEN CHAT
    # ========================================================

    def open_chat(
        self,
        chat_id
    ):

        if self.is_generating:

            return


        success = switch_chat(
            chat_id
        )


        if not success:

            return


        active_chat = get_active_chat()


        if not active_chat:

            return


        self.load_chat_into_gui(
            active_chat
        )


        self.refresh_history()


    # ========================================================
    # LOAD CHAT
    # ========================================================

    def load_chat_into_gui(
        self,
        chat
    ):

        # Clear messages

        for widget in self.messages.winfo_children():

            widget.destroy()


        # Reset streaming

        self.streaming_row = None

        self.streaming_bubble = None

        self.streaming_content = None


        chat_messages = chat.get(
            "messages",
            []
        )


        # ----------------------------------------------------
        # Empty chat
        # ----------------------------------------------------

        if not chat_messages:

            self.create_welcome_screen()


        # ----------------------------------------------------
        # Existing chat
        # ----------------------------------------------------

        else:

            for index, message in enumerate(
                chat_messages
            ):

                role = message.get(
                    "role"
                )


                content = message.get(
                    "content",
                    ""
                )


                if role == "user":

                    self.add_message(
                        content,
                        "You",
                        is_user=True,
                        message_index=index
                    )


                elif role == "assistant":

                    self.add_message(
                        content,
                        "EldhoAi",
                        is_user=False,
                        message_index=index
                    )


        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        self.title_label.configure(
            text=chat.get(
                "title",
                "EldhoAi"
            )
        )


        # ----------------------------------------------------
        # Status
        # ----------------------------------------------------

        self.status_label.configure(
            text="●  Online",
            text_color="#4ade80"
        )


        self.scroll_to_bottom()


    # ========================================================
    # REFRESH HISTORY
    # ========================================================

    # ========================================================
    # REFRESH CHAT HISTORY
    # ========================================================

    def refresh_history(self):

        # Remove existing history items

        for widget in self.history_list.winfo_children():
            widget.destroy()

        self.history_buttons = []

        # Get saved chats

        chats = get_saved_chats()

        active_chat = get_active_chat()

        active_id = (
            active_chat.get("id")
            if active_chat
            else None
        )

        # Display newest chats first

        for chat in reversed(chats):

            chat_id = chat.get("id")

            title = chat.get(
                "title",
                "New Chat"
            )

            if not chat_id:
                continue

            # Shorten long titles for display only.
            # The actual saved chat title remains unchanged.

            display_title = (
                title
                if len(title) <= 18
                else title[:17].rstrip() + "…"
            )

            # ----------------------------------------------------
            # CHAT ROW
            # ----------------------------------------------------

            row = ctk.CTkFrame(
                self.history_list,
                fg_color=(
                    self.active_chat_color
                    if chat_id == active_id
                    else "transparent"
                ),
                corner_radius=8
            )

            row.pack(
                fill="x",
                padx=6,
                pady=2
            )

            # Reserve space for the action button

            row.grid_columnconfigure(
                0,
                weight=1
            )

            row.grid_columnconfigure(
                1,
                weight=0
            )

            # ----------------------------------------------------
            # CHAT TITLE BUTTON
            # ----------------------------------------------------

            chat_button = ctk.CTkButton(
                row,
                text="💬  " + display_title,
                width=1,
                height=36,
                fg_color="transparent",
                hover_color=(
                    self.active_chat_hover
                    if chat_id == active_id
                    else "#24272d"
                ),
                anchor="w",
                corner_radius=8,
                font=ctk.CTkFont(
                    size=12
                ),
                command=lambda cid=chat_id:
                self.open_chat(cid)
            )

            chat_button.grid(
                row=0,
                column=0,
                sticky="ew",
                padx=(3, 0),
                pady=2
            )

            # ----------------------------------------------------
            # CHAT ACTION BUTTON
            # ----------------------------------------------------

            action_button = ctk.CTkButton(
                row,
                text="⋯",
                width=30,
                height=30,
                corner_radius=7,
                fg_color="transparent",
                hover_color="#343840",
                font=ctk.CTkFont(
                    size=20,
                    weight="bold"
                ),
                command=lambda cid=chat_id:
                self.show_chat_actions(cid)
            )

            action_button.grid(
                row=0,
                column=1,
                sticky="e",
                padx=(0, 4),
                pady=2
            )

            # Keep references for enabling/disabling controls

            self.history_buttons.append(
                {
                    "chat_button": chat_button,
                    "action_button": action_button,
                    "chat_id": chat_id
                }
            )


    # ========================================================
    # CHAT ACTIONS
    # ========================================================

    def show_chat_actions(
        self,
        chat_id
    ):

        if self.is_generating:

            return


        popup = ctk.CTkToplevel(
            self
        )

        popup.title(
            "Chat Options"
        )

        popup.geometry(
            "300x200"
        )

        popup.resizable(
            False,
            False
        )

        popup.transient(
            self
        )

        popup.grab_set()


        title = ctk.CTkLabel(
            popup,
            text="Chat Options",
            font=ctk.CTkFont(
                size=20,
                weight="bold"
            )
        )

        title.pack(
            pady=(25, 15)
        )


        rename_button = ctk.CTkButton(
            popup,
            text="✏  Rename Chat",
            height=40,
            corner_radius=10,
            command=lambda:
                self.start_rename(
                    chat_id,
                    popup
                )
        )

        rename_button.pack(
            padx=35,
            pady=5,
            fill="x"
        )


        delete_button = ctk.CTkButton(
            popup,
            text="🗑  Delete Chat",
            height=40,
            corner_radius=10,
            fg_color="#9f3030",
            hover_color="#b83b3b",
            command=lambda:
                self.start_delete(
                    chat_id,
                    popup
                )
        )

        delete_button.pack(
            padx=35,
            pady=5,
            fill="x"
        )


    # ========================================================
    # RENAME CHAT
    # ========================================================

    def start_rename(
        self,
        chat_id,
        parent_popup=None
    ):

        if parent_popup:

            parent_popup.destroy()


        chat = next(
            (
                chat
                for chat in get_saved_chats()
                if chat.get("id") == chat_id
            ),
            None
        )


        if not chat:

            return


        dialog = ctk.CTkToplevel(
            self
        )

        dialog.title(
            "Rename Chat"
        )

        dialog.geometry(
            "420x220"
        )

        dialog.resizable(
            False,
            False
        )

        dialog.transient(
            self
        )

        dialog.grab_set()


        title = ctk.CTkLabel(
            dialog,
            text="Rename Chat",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        title.pack(
            pady=(25, 15)
        )


        entry = ctk.CTkEntry(
            dialog,
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(
                size=14
            )
        )

        entry.pack(
            padx=30,
            fill="x"
        )


        entry.insert(
            0,
            chat.get(
                "title",
                "New Chat"
            )
        )

        entry.select_range(
            0,
            "end"
        )

        entry.focus()


        def save():

            new_title = entry.get().strip()


            if not new_title:

                return


            rename_chat(
                chat_id,
                new_title
            )


            dialog.destroy()


            self.refresh_history()


            active_chat = get_active_chat()


            if (
                active_chat
                and active_chat.get(
                    "id"
                ) == chat_id
            ):

                self.title_label.configure(
                    text=new_title
                )


        save_button = ctk.CTkButton(
            dialog,
            text="Save",
            height=40,
            corner_radius=10,
            command=save
        )

        save_button.pack(
            padx=30,
            pady=18,
            fill="x"
        )


        entry.bind(
            "<Return>",
            lambda event:
                save()
        )


    # ========================================================
    # DELETE CHAT
    # ========================================================

    def start_delete(
        self,
        chat_id,
        parent_popup=None
    ):

        if parent_popup:

            parent_popup.destroy()


        confirm = ctk.CTkToplevel(
            self
        )

        confirm.title(
            "Delete Chat"
        )

        confirm.geometry(
            "430x240"
        )

        confirm.resizable(
            False,
            False
        )

        confirm.transient(
            self
        )

        confirm.grab_set()


        title = ctk.CTkLabel(
            confirm,
            text="Delete this chat?",
            font=ctk.CTkFont(
                size=22,
                weight="bold"
            )
        )

        title.pack(
            pady=(30, 10)
        )


        text = ctk.CTkLabel(
            confirm,
            text="This conversation will be permanently removed.",
            text_color="#9da1aa",
            font=ctk.CTkFont(
                size=13
            )
        )

        text.pack(
            pady=5
        )


        buttons = ctk.CTkFrame(
            confirm,
            fg_color="transparent"
        )

        buttons.pack(
            fill="x",
            padx=30,
            pady=25
        )


        cancel_button = ctk.CTkButton(
            buttons,
            text="Cancel",
            height=40,
            corner_radius=10,
            fg_color="#30333a",
            hover_color="#3b3f47",
            command=confirm.destroy
        )

        cancel_button.pack(
            side="left",
            expand=True,
            fill="x",
            padx=(0, 6)
        )


        def delete():

            active_chat = get_active_chat()


            deleted_active = (
                active_chat is not None
                and active_chat.get(
                    "id"
                ) == chat_id
            )


            remove_chat(
                chat_id
            )


            confirm.destroy()


            if deleted_active:

                for widget in self.messages.winfo_children():

                    widget.destroy()


                self.create_welcome_screen()


                self.title_label.configure(
                    text="EldhoAi"
                )


            self.refresh_history()


        delete_button = ctk.CTkButton(
            buttons,
            text="Delete",
            height=40,
            corner_radius=10,
            fg_color="#9f3030",
            hover_color="#b83b3b",
            command=delete
        )

        delete_button.pack(
            side="right",
            expand=True,
            fill="x",
            padx=(6, 0)
        )


    # ========================================================
    # NEW CHAT
    # ========================================================

    def new_chat(self):

        if self.is_generating:

            return


        start_new_chat()


        for widget in self.messages.winfo_children():

            widget.destroy()


        self.streaming_row = None

        self.streaming_bubble = None

        self.streaming_content = None


        self.create_welcome_screen()


        self.title_label.configure(
            text="EldhoAi"
        )


        self.status_label.configure(
            text="●  Online",
            text_color="#4ade80"
        )


        self.refresh_history()


        self.message_entry._textbox.focus_set()


    # ========================================================
    # MARKDOWN
    # ========================================================

    def insert_markdown(
        self,
        parent,
        text,
        is_user=False
    ):

        max_width = (
            480
            if is_user
            else 720
        )

        # Respect the Markdown preference.

        if not load_settings().get("render_markdown", True):
            plain_label = ctk.CTkLabel(
                parent,
                text=text,
                font=ctk.CTkFont(size=14),
                anchor="w",
                justify="left",
                wraplength=max_width
            )

            plain_label.pack(
                fill="x",
                anchor="w",
                pady=2
            )

            return


        lines = text.split(
            "\n"
        )


        for line in lines:

            # ------------------------------------------------
            # Empty line
            # ------------------------------------------------

            if not line.strip():

                spacer = ctk.CTkLabel(
                    parent,
                    text="",
                    height=8
                )

                spacer.pack(
                    fill="x"
                )

                continue


            # ------------------------------------------------
            # H1
            # ------------------------------------------------

            if (
                line.startswith("# ")
                and not line.startswith("## ")
            ):

                heading = ctk.CTkLabel(
                    parent,
                    text=line[2:].strip(),
                    font=ctk.CTkFont(
                        size=24,
                        weight="bold"
                    ),
                    anchor="w",
                    justify="left",
                    wraplength=max_width
                )

                heading.pack(
                    fill="x",
                    anchor="w",
                    pady=(8, 6)
                )

                continue


            # ------------------------------------------------
            # H2
            # ------------------------------------------------

            if (
                line.startswith("## ")
                and not line.startswith("### ")
            ):

                heading = ctk.CTkLabel(
                    parent,
                    text=line[3:].strip(),
                    font=ctk.CTkFont(
                        size=20,
                        weight="bold"
                    ),
                    anchor="w",
                    justify="left",
                    wraplength=max_width
                )

                heading.pack(
                    fill="x",
                    anchor="w",
                    pady=(8, 5)
                )

                continue


            # ------------------------------------------------
            # H3
            # ------------------------------------------------

            if line.startswith("### "):

                heading = ctk.CTkLabel(
                    parent,
                    text=line[4:].strip(),
                    font=ctk.CTkFont(
                        size=17,
                        weight="bold"
                    ),
                    anchor="w",
                    justify="left",
                    wraplength=max_width
                )

                heading.pack(
                    fill="x",
                    anchor="w",
                    pady=(7, 4)
                )

                continue


            # ------------------------------------------------
            # Separator
            # ------------------------------------------------

            if line.strip() in (
                "---",
                "***",
                "___"
            ):

                separator = ctk.CTkLabel(
                    parent,
                    text="────────────────────────────",
                    font=ctk.CTkFont(
                        size=12
                    ),
                    text_color="#777b84",
                    anchor="w"
                )

                separator.pack(
                    anchor="w",
                    pady=5
                )

                continue


            # ------------------------------------------------
            # Bullet
            # ------------------------------------------------

            if (
                line.startswith("- ")
                or line.startswith("* ")
            ):

                self.create_rich_label(
                    parent,
                    "• " + line[2:].strip(),
                    max_width,
                    is_user,
                    left_padding=8
                )

                continue


            # ------------------------------------------------
            # Numbered list
            # ------------------------------------------------

            numbered_match = re.match(
                r"^(\d+)\.\s+(.*)",
                line
            )


            if numbered_match:

                number = numbered_match.group(
                    1
                )

                content = numbered_match.group(
                    2
                )


                self.create_rich_label(
                    parent,
                    f"{number}. {content}",
                    max_width,
                    is_user,
                    left_padding=8
                )

                continue


            # ------------------------------------------------
            # Normal
            # ------------------------------------------------

            self.create_rich_label(
                parent,
                line,
                max_width,
                is_user
            )


    # ========================================================
    # RICH LABEL
    # ========================================================

    def create_rich_label(
        self,
        parent,
        text,
        max_width,
        is_user=False,
        left_padding=0
    ):
        """Render inline Markdown while wrapping long lines correctly.

        Previously, bold/code fragments were packed side-by-side in a single
        frame. That made mixed-format paragraphs overflow horizontally instead
        of wrapping. This version measures words and builds wrapped rows.
        """
        parts = re.split(r"(\*\*.*?\*\*|`.*?`)", text)

        # Plain text already wraps correctly in one label.
        if len(parts) == 1:
            label = ctk.CTkLabel(
                parent,
                text=text,
                font=ctk.CTkFont(size=14),
                anchor="w",
                justify="left",
                wraplength=max_width
            )
            label.pack(
                fill="x",
                anchor="w",
                padx=(left_padding, 0),
                pady=2
            )
            return

        fonts = {
            "normal": ctk.CTkFont(size=14),
            "bold": ctk.CTkFont(size=14, weight="bold"),
            "code": ctk.CTkFont(family="Consolas", size=13),
        }
        # Reserve room for the bubble's interior padding and widget sizing.
        available_width = max(80, int(max_width) - 24)
        rows = []
        row_tokens = []
        row_width = 0

        def measured_width(value, style):
            extra = 12 if style == "code" else 0
            return fonts[style].measure(value) + extra

        def add_piece(value, style):
            nonlocal row_tokens, row_width
            if not value:
                return

            value_width = measured_width(value, style)
            if row_tokens and row_width + value_width > available_width:
                rows.append(row_tokens)
                row_tokens = []
                row_width = 0
                value = value.lstrip()
                if not value:
                    return
                value_width = measured_width(value, style)

            # Break unusually long unspaced words/URLs so they cannot force
            # the whole message bubble wider than its intended width.
            if value_width > available_width:
                chunk = ""
                for character in value:
                    if chunk and measured_width(chunk + character, style) > available_width:
                        if row_tokens:
                            rows.append(row_tokens)
                            row_tokens = []
                            row_width = 0
                        row_tokens.append((style, chunk))
                        rows.append(row_tokens)
                        row_tokens = []
                        row_width = 0
                        chunk = character
                    else:
                        chunk += character
                if chunk:
                    value = chunk
                    value_width = measured_width(value, style)
                else:
                    return

            row_tokens.append((style, value))
            row_width += value_width

        for part in parts:
            if not part:
                continue

            if part.startswith("**") and part.endswith("**"):
                style = "bold"
                content = part[2:-2]
            elif part.startswith("`") and part.endswith("`"):
                style = "code"
                content = part[1:-1]
            else:
                style = "normal"
                content = part

            # Keep spaces with their following word so words retain spacing
            # when separate font styles are placed in neighboring labels.
            tokens = re.findall(r"\s*\S+\s*", content)
            for token in tokens:
                if not token.strip():
                    continue
                add_piece(token, style)

        if row_tokens:
            rows.append(row_tokens)

        for row in rows:
            line_frame = ctk.CTkFrame(
                parent,
                fg_color="transparent"
            )
            line_frame.pack(
                fill="x",
                anchor="w",
                padx=(left_padding, 0),
                pady=2
            )

            # Merge adjacent tokens of the same style into one label to keep
            # widget counts low even for long responses.
            groups = []
            for style, token in row:
                if groups and groups[-1][0] == style:
                    groups[-1] = (style, groups[-1][1] + token)
                else:
                    groups.append((style, token))

            for style, group_text in groups:
                if not group_text:
                    continue
                options = {
                    "master": line_frame,
                    "text": group_text,
                    "font": fonts[style],
                    "anchor": "w",
                    "justify": "left",
                }
                if style == "code":
                    options.update({
                        "fg_color": "#111318",
                        "corner_radius": 5,
                        "padx": 5,
                        "pady": 2,
                    })
                label = ctk.CTkLabel(**options)
                label.pack(
                    side="left",
                    padx=(0, 2) if style == "code" else 0
                )


    # ========================================================
    # SCROLL
    # ========================================================

    # ========================================================
    # SCROLL TO BOTTOM
    # ========================================================

    def scroll_to_bottom(self):

        settings = load_settings()

        if not settings.get("auto_scroll", True):
            return

        try:
            self.messages._parent_canvas.yview_moveto(1.0)

        except Exception:
            pass


    # ========================================================
    # SETTINGS
    # ========================================================

    # ========================================================
    # ELDHOAI CONTROL CENTER
    # ========================================================

    def open_settings(self):

        # Don't change settings while generating a response.

        if self.is_generating:
            return

        current = load_settings()

        # ====================================================
        # WINDOW
        # ====================================================

        settings_window = ctk.CTkToplevel(self)

        settings_window.title("EldhoAi Control Center")

        settings_window.geometry("570x700")

        settings_window.minsize(520, 600)

        settings_window.transient(self)

        settings_window.grab_set()

        settings_window.grid_rowconfigure(1, weight=1)

        settings_window.grid_columnconfigure(0, weight=1)

        # ====================================================
        # HEADER
        # ====================================================

        header = ctk.CTkFrame(
            settings_window,
            fg_color="transparent"
        )

        header.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=22,
            pady=(20, 10)
        )

        title = ctk.CTkLabel(
            header,
            text="⚙  EldhoAi Control Center",
            font=ctk.CTkFont(
                size=25,
                weight="bold"
            )
        )

        title.pack(anchor="w")

        subtitle = ctk.CTkLabel(
            header,
            text="Customize your AI and application experience.",
            text_color="#9699a3",
            font=ctk.CTkFont(size=13)
        )

        subtitle.pack(
            anchor="w",
            pady=(5, 0)
        )

        # ====================================================
        # SCROLLABLE SETTINGS CONTENT
        # ====================================================

        content = ctk.CTkScrollableFrame(
            settings_window,
            fg_color="transparent"
        )

        content.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=15,
            pady=5
        )

        # ====================================================
        # HELPER FUNCTIONS
        # ====================================================

        def add_section(text):

            label = ctk.CTkLabel(
                content,
                text=text,
                font=ctk.CTkFont(
                    size=17,
                    weight="bold"
                )
            )

            label.pack(
                anchor="w",
                padx=8,
                pady=(18, 8)
            )

        def add_label(text):

            label = ctk.CTkLabel(
                content,
                text=text,
                font=ctk.CTkFont(size=13),
                text_color="#b8bcc6"
            )

            label.pack(
                anchor="w",
                padx=8,
                pady=(8, 4)
            )

            return label

        def add_option_menu(
                label_text,
                values,
                selected
        ):

            add_label(label_text)

            menu = ctk.CTkOptionMenu(
                content,
                values=values,
                height=38,
                corner_radius=9
            )

            menu.pack(
                fill="x",
                padx=8,
                pady=(0, 5)
            )

            menu.set(str(selected))

            return menu

        # ====================================================
        # AI CONFIGURATION
        # ====================================================

        add_section("🤖 AI Configuration")

        # ----------------------------------------------------
        # MODEL
        # ----------------------------------------------------

        model_labels = {
            "GLM-5.3 Flash (Recommended)": "z-ai/glm-5.3-flash",
            "GLM-5.3": "z-ai/glm-5.3"
        }

        saved_model = current.get(
            "model",
            "z-ai/glm-5.3-flash"
        )

        selected_model_label = next(
            (
                label
                for label, model_id in model_labels.items()
                if model_id == saved_model
            ),
            "GLM-5.3 Flash (Recommended)"
        )

        model_menu = add_option_menu(
            "AI Model",
            list(model_labels.keys()),
            selected_model_label
        )

        # ----------------------------------------------------
        # REASONING
        # ----------------------------------------------------

        reasoning_menu = add_option_menu(
            "Reasoning Effort",
            ["low", "high", "max"],
            current.get("reasoning_effort", "low")
        )

        # ----------------------------------------------------
        # TEMPERATURE
        # ----------------------------------------------------

        add_label("Temperature")

        temperature_frame = ctk.CTkFrame(
            content,
            fg_color="transparent"
        )

        temperature_frame.pack(
            fill="x",
            padx=8,
            pady=3
        )

        temperature = ctk.CTkSlider(
            temperature_frame,
            from_=0.0,
            to=1.0,
            number_of_steps=20
        )

        temperature.pack(
            side="left",
            fill="x",
            expand=True,
            padx=(0, 12)
        )

        temperature_value = ctk.CTkLabel(
            temperature_frame,
            text="0.50",
            width=45,
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            )
        )

        temperature_value.pack(side="right")

        temperature.set(
            float(current.get("temperature", 0.5))
        )

        temperature_value.configure(
            text=f"{temperature.get():.2f}"
        )

        def update_temperature(value):

            temperature_value.configure(
                text=f"{float(value):.2f}"
            )

        temperature.configure(
            command=update_temperature
        )

        # ----------------------------------------------------
        # MAXIMUM RESPONSE LENGTH
        # ----------------------------------------------------

        token_menu = add_option_menu(
            "Maximum Response Length",
            ["512", "1024", "2048", "4096"],
            current.get("max_tokens", 1024)
        )

        token_description = ctk.CTkLabel(
            content,
            text="Higher limits allow longer answers but may increase generation time.",
            font=ctk.CTkFont(size=11),
            text_color="#858993",
            wraplength=480,
            justify="left"
        )

        token_description.pack(
            anchor="w",
            padx=8,
            pady=(0, 5)
        )

        # ====================================================
        # APPEARANCE
        # ====================================================

        add_section("🎨 Appearance")

        appearance_menu = add_option_menu(
            "Theme",
            ["dark", "light", "system"],
            current.get("appearance", "dark")
        )

        scale_menu = add_option_menu(
            "Interface Scale",
            ["0.8", "0.9", "1.0", "1.1", "1.2"],
            current.get("ui_scale", 1.0)
        )

        # ====================================================
        # CHAT BEHAVIOR
        # ====================================================

        add_section("💬 Chat Behavior")

        # ----------------------------------------------------
        # ENTER TO SEND
        # ----------------------------------------------------

        enter_switch = ctk.CTkSwitch(
            content,
            text="Press Enter to send messages"
        )

        enter_switch.pack(
            anchor="w",
            padx=8,
            pady=9
        )

        if current.get("enter_to_send", True):
            enter_switch.select()
        else:
            enter_switch.deselect()

        # ----------------------------------------------------
        # AUTO-SCROLL
        # ----------------------------------------------------

        scroll_switch = ctk.CTkSwitch(
            content,
            text="Automatically scroll to new responses"
        )

        scroll_switch.pack(
            anchor="w",
            padx=8,
            pady=9
        )

        if current.get("auto_scroll", True):
            scroll_switch.select()
        else:
            scroll_switch.deselect()

        # ----------------------------------------------------
        # MARKDOWN
        # ----------------------------------------------------

        markdown_switch = ctk.CTkSwitch(
            content,
            text="Render Markdown formatting"
        )

        markdown_switch.pack(
            anchor="w",
            padx=8,
            pady=9
        )

        if current.get("render_markdown", True):
            markdown_switch.select()
        else:
            markdown_switch.deselect()

        # ----------------------------------------------------
        # VOICE REPLIES
        # ----------------------------------------------------

        voice_switch = ctk.CTkSwitch(
            content,
            text="Read AI responses aloud"
        )
        voice_switch.pack(
            anchor="w",
            padx=8,
            pady=9
        )
        if current.get("voice_replies", False):
            voice_switch.select()
        else:
            voice_switch.deselect()

        voice_description = ctk.CTkLabel(
            content,
            text="Uses your computer's speech engine. Click the speaker button to stop playback.",
            font=ctk.CTkFont(size=11),
            text_color="#858993",
            wraplength=480,
            justify="left"
        )
        voice_description.pack(
            anchor="w",
            padx=8,
            pady=(0, 5)
        )

        # ====================================================
        # STATUS MESSAGE
        # ====================================================

        save_status = ctk.CTkLabel(
            settings_window,
            text="Changes are applied when you save.",
            text_color="#9699a3",
            font=ctk.CTkFont(size=11)
        )

        save_status.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=(5, 0)
        )

        # ====================================================
        # BUTTONS
        # ====================================================

        footer = ctk.CTkFrame(
            settings_window,
            fg_color="transparent"
        )

        footer.grid(
            row=3,
            column=0,
            sticky="ew",
            padx=20,
            pady=15
        )

        footer.grid_columnconfigure(
            0,
            weight=1
        )

        footer.grid_columnconfigure(
            1,
            weight=1
        )

        # ====================================================
        # SAVE SETTINGS
        # ====================================================

        def save_all_settings():

            selected_model = model_labels[
                model_menu.get()
            ]

            updated = {
                "model": selected_model,

                "reasoning_effort": reasoning_menu.get(),

                "temperature": round(
                    float(temperature.get()),
                    2
                ),

                "max_tokens": int(
                    token_menu.get()
                ),

                "appearance": appearance_menu.get(),

                "ui_scale": float(
                    scale_menu.get()
                ),

                "enter_to_send": bool(
                    enter_switch.get()
                ),

                "auto_scroll": bool(
                    scroll_switch.get()
                ),

                "render_markdown": bool(
                    markdown_switch.get()
                ),

                "voice_replies": bool(
                    voice_switch.get()
                )
            }

            if not save_settings(updated):
                save_status.configure(
                    text="Unable to save settings. Check the data folder.",
                    text_color="#ef4444"
                )

                return

            # Apply saved appearance.

            ctk.set_appearance_mode(
                updated["appearance"]
            )

            ctk.set_widget_scaling(
                updated["ui_scale"]
            )

            settings_window.destroy()

            self.status_label.configure(
                text="●  Settings saved",
                text_color="#60a5fa"
            )

            self.after(
                1500,
                lambda: self.status_label.configure(
                    text="●  Online",
                    text_color="#4ade80"
                )
            )

        # ====================================================
        # SAVE BUTTON
        # ====================================================

        save_button = ctk.CTkButton(
            footer,
            text="Save Settings",
            height=42,
            corner_radius=10,
            font=ctk.CTkFont(
                size=13,
                weight="bold"
            ),
            command=save_all_settings
        )

        save_button.grid(
            row=0,
            column=0,
            sticky="ew",
            padx=(0, 6)
        )

        # ====================================================
        # CANCEL BUTTON
        # ====================================================

        cancel_button = ctk.CTkButton(
            footer,
            text="Cancel",
            height=42,
            corner_radius=10,
            fg_color="#30333a",
            hover_color="#3b3f47",
            command=settings_window.destroy
        )

        cancel_button.grid(
            row=0,
            column=1,
            sticky="ew",
            padx=(6, 0)
        )


    # ========================================================
    # EXPORT CHAT
    # ========================================================

    def export_chat(self):

        # Avoid exporting while the conversation is actively changing.
        if self.is_generating:
            messagebox.showinfo(
                "Response in progress",
                "Wait for EldhoAi to finish responding before exporting this chat.",
                parent=self
            )
            return

        chat = get_active_chat()

        if not chat:
            messagebox.showinfo(
                "No chat to export",
                "Create or open a conversation before exporting it.",
                parent=self
            )
            return

        messages = chat.get("messages", [])

        if not messages:
            messagebox.showinfo(
                "Empty conversation",
                "This conversation does not contain any messages to export yet.",
                parent=self
            )
            return

        title = str(chat.get("title") or "EldhoAi Chat").strip()
        if not title:
            title = "EldhoAi Chat"

        # Create a Windows-safe suggested filename.
        safe_filename = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "", title)
        safe_filename = safe_filename.strip().rstrip(". ")[:80]
        if not safe_filename:
            safe_filename = "EldhoAi Chat"

        file_path = filedialog.asksaveasfilename(
            parent=self,
            title="Export EldhoAi Chat",
            initialfile=f"{safe_filename}.md",
            defaultextension=".md",
            filetypes=[
                ("Markdown document (*.md)", "*.md"),
                ("Plain text document (*.txt)", "*.txt")
            ]
        )

        if not file_path:
            return

        extension = os.path.splitext(file_path)[1].lower()
        if extension not in (".md", ".txt"):
            file_path += ".md"
            extension = ".md"

        # Normalize each saved message into readable speaker/content blocks.
        blocks = []
        for saved_message in messages:
            role = str(saved_message.get("role", "")).lower()
            content = saved_message.get("content", "")
            if not isinstance(content, str):
                content = str(content)

            if role == "user":
                speaker = "You"
            elif role == "assistant":
                speaker = "EldhoAi"
            elif role == "system":
                speaker = "System"
            else:
                speaker = role.capitalize() if role else "Message"

            if extension == ".md":
                blocks.append(f"## {speaker}\n\n{content.strip()}")
            else:
                blocks.append(f"{speaker}\n{'-' * len(speaker)}\n{content.strip()}")

        if extension == ".md":
            export_text = (
                f"# {title}\n\n"
                "Exported from EldhoAi\n\n"
                + "\n\n---\n\n".join(blocks)
                + "\n"
            )
        else:
            export_text = (
                f"{title}\n{'=' * len(title)}\n\n"
                "Exported from EldhoAi\n\n"
                + "\n\n".join(blocks)
                + "\n"
            )

        try:
            with open(file_path, "w", encoding="utf-8", newline="\n") as export_file:
                export_file.write(export_text)
        except OSError as error:
            messagebox.showerror(
                "Export failed",
                f"EldhoAi could not save the conversation.\n\n{error}",
                parent=self
            )
            return

        self.status_label.configure(
            text="●  Chat exported",
            text_color="#60a5fa"
        )
        self.after(
            1800,
            lambda: self.restore_status("●  Online", "#4ade80")
        )

        messagebox.showinfo(
            "Export complete",
            f"Your conversation was exported successfully to:\n\n{file_path}",
            parent=self
        )


    # ========================================================
    # APPEARANCE
    # ========================================================

    def change_appearance(
        self,
        choice
    ):

        ctk.set_appearance_mode(
            choice.lower()
        )


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    app = EldhoAiApp()

    app.mainloop()
