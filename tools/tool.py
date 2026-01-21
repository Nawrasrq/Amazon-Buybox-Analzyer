# Tkinter GUI for Amazon Buy Box Analyzer
# Provides user interface for ASIN input, credential management, and analysis execution

import logging
import os
import re
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import List, Optional

from dotenv import load_dotenv

from scripts.buybox_analyzer import BuyBoxAnalyzer


class Tool:
    """
    Main GUI application for Amazon Buy Box Analyzer.

    Provides a two-tab interface:
    - Credentials: Configure and save SP-API credentials
    - Analyze: Input ASINs and run Buy Box analysis
    """

    def __init__(self, log_file_path: str = "tool/tool.log"):
        """
        Initialize the tool.

        Parameters
        ----------
        log_file_path : str, optional
            Path to log file relative to logs/ directory
        """
        # Setup logging directory
        log_dir = os.path.dirname(log_file_path)
        if log_dir:
            full_log_dir = os.path.join("logs", log_dir)
            os.makedirs(full_log_dir, exist_ok=True)

        # Initialize analyzer
        self.analyzer = BuyBoxAnalyzer(log_file_path)
        self.logger = logging.getLogger(f"tools.tool.instance_{self.analyzer.instance_id}")

        # State
        self.is_analyzing = False
        self.analysis_thread: Optional[threading.Thread] = None

        # Create GUI
        self.root: tk.Tk = self.create_gui()

        self.logger.info("Initialized Tool class")

    # MARK: GUI Creation
    def create_gui(self) -> tk.Tk:
        """Create the main GUI window and all widgets."""
        self.root = tk.Tk()
        self.root.title("Amazon Buy Box Analyzer")
        self.root.geometry("850x750")
        self.root.minsize(700, 600)

        # Configure grid weight for resizing
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        # Credentials Tab
        self.credentials_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.credentials_frame, text="Credentials")
        self._create_credentials_tab()

        # Analyze Tab
        self.analyze_frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(self.analyze_frame, text="Analyze")
        self._create_analyze_tab()

        # Load existing credentials
        self._load_existing_credentials()

        return self.root

    def _create_credentials_tab(self) -> None:
        """Create the credentials configuration tab."""
        # Title
        title_label = ttk.Label(
            self.credentials_frame,
            text="SP-API Credentials",
            font=("Segoe UI", 14, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 10))

        # Instructions
        instructions = ttk.Label(
            self.credentials_frame,
            text="Enter your Amazon Selling Partner API credentials below.\n"
                 "These are saved to .env file and loaded automatically on startup.",
            foreground="gray"
        )
        instructions.grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 20))

        # Refresh Token
        ttk.Label(self.credentials_frame, text="Refresh Token:").grid(
            row=2, column=0, sticky="w", pady=5
        )
        self.refresh_token_var = tk.StringVar()
        self.refresh_token_entry = ttk.Entry(
            self.credentials_frame,
            textvariable=self.refresh_token_var,
            width=60,
            show="*"
        )
        self.refresh_token_entry.grid(row=2, column=1, sticky="ew", pady=5, padx=(10, 0))

        # Client ID
        ttk.Label(self.credentials_frame, text="Client ID:").grid(
            row=3, column=0, sticky="w", pady=5
        )
        self.client_id_var = tk.StringVar()
        self.client_id_entry = ttk.Entry(
            self.credentials_frame,
            textvariable=self.client_id_var,
            width=60
        )
        self.client_id_entry.grid(row=3, column=1, sticky="ew", pady=5, padx=(10, 0))

        # Client Secret
        ttk.Label(self.credentials_frame, text="Client Secret:").grid(
            row=4, column=0, sticky="w", pady=5
        )
        self.client_secret_var = tk.StringVar()
        self.client_secret_entry = ttk.Entry(
            self.credentials_frame,
            textvariable=self.client_secret_var,
            width=60,
            show="*"
        )
        self.client_secret_entry.grid(row=4, column=1, sticky="ew", pady=5, padx=(10, 0))

        # Show/Hide password toggle
        self.show_credentials_var = tk.BooleanVar(value=False)
        show_check = ttk.Checkbutton(
            self.credentials_frame,
            text="Show credentials",
            variable=self.show_credentials_var,
            command=self._toggle_credential_visibility
        )
        show_check.grid(row=5, column=1, sticky="w", padx=(10, 0), pady=5)

        # Buttons frame
        btn_frame = ttk.Frame(self.credentials_frame)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=20)

        self.test_btn = ttk.Button(
            btn_frame,
            text="Test Connection",
            command=self.test_connection
        )
        self.test_btn.pack(side="left", padx=5)

        self.save_btn = ttk.Button(
            btn_frame,
            text="Save to .env",
            command=self.save_credentials
        )
        self.save_btn.pack(side="left", padx=5)

        # Status label
        self.credentials_status_var = tk.StringVar(value="Status: Not configured")
        self.credentials_status = ttk.Label(
            self.credentials_frame,
            textvariable=self.credentials_status_var,
            foreground="gray"
        )
        self.credentials_status.grid(row=7, column=0, columnspan=2, sticky="w", pady=10)

        # Configure column weights
        self.credentials_frame.grid_columnconfigure(1, weight=1)

    def _create_analyze_tab(self) -> None:
        """Create the analysis tab with ASIN input and controls."""
        # Configure grid weights for resizing
        self.analyze_frame.grid_rowconfigure(1, weight=1)
        self.analyze_frame.grid_rowconfigure(6, weight=1)
        self.analyze_frame.grid_columnconfigure(0, weight=1)

        # ASIN Input Section
        asin_label = ttk.Label(
            self.analyze_frame,
            text="Enter ASINs (one per line):",
            font=("Segoe UI", 11, "bold")
        )
        asin_label.grid(row=0, column=0, sticky="w", pady=(0, 5))

        # ASIN Text Area with scrollbar
        asin_frame = ttk.Frame(self.analyze_frame)
        asin_frame.grid(row=1, column=0, sticky="nsew", pady=5)
        asin_frame.grid_rowconfigure(0, weight=1)
        asin_frame.grid_columnconfigure(0, weight=1)

        self.asin_text = tk.Text(asin_frame, height=10, width=50, wrap="none")
        asin_scrollbar = ttk.Scrollbar(asin_frame, orient="vertical", command=self.asin_text.yview)
        self.asin_text.configure(yscrollcommand=asin_scrollbar.set)

        self.asin_text.grid(row=0, column=0, sticky="nsew")
        asin_scrollbar.grid(row=0, column=1, sticky="ns")

        # Bind text change event
        self.asin_text.bind("<KeyRelease>", self._update_asin_count)

        # ASIN count and clear button
        count_frame = ttk.Frame(self.analyze_frame)
        count_frame.grid(row=2, column=0, sticky="ew", pady=5)

        self.asin_count_var = tk.StringVar(value="ASINs to analyze: 0")
        asin_count_label = ttk.Label(count_frame, textvariable=self.asin_count_var)
        asin_count_label.pack(side="left")

        clear_btn = ttk.Button(count_frame, text="Clear", command=self._clear_asins)
        clear_btn.pack(side="right")

        # Output file section
        output_frame = ttk.Frame(self.analyze_frame)
        output_frame.grid(row=3, column=0, sticky="ew", pady=10)
        output_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(output_frame, text="Output File:").grid(row=0, column=0, sticky="w")

        self.output_path_var = tk.StringVar(value="buybox_analysis.xlsx")
        self.output_entry = ttk.Entry(output_frame, textvariable=self.output_path_var)
        self.output_entry.grid(row=0, column=1, sticky="ew", padx=10)

        browse_btn = ttk.Button(output_frame, text="Browse", command=self._browse_output)
        browse_btn.grid(row=0, column=2)

        # Analyze button
        self.analyze_btn = ttk.Button(
            self.analyze_frame,
            text="Analyze Buy Box",
            command=self.start_analysis,
            style="Accent.TButton"
        )
        self.analyze_btn.grid(row=4, column=0, pady=15)

        # Progress section
        progress_frame = ttk.Frame(self.analyze_frame)
        progress_frame.grid(row=5, column=0, sticky="ew", pady=5)
        progress_frame.grid_columnconfigure(0, weight=1)

        self.progress_var = tk.DoubleVar(value=0)
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.grid(row=0, column=0, sticky="ew")

        self.analysis_status_var = tk.StringVar(value="Ready")
        analysis_status = ttk.Label(progress_frame, textvariable=self.analysis_status_var)
        analysis_status.grid(row=1, column=0, sticky="w", pady=5)

        # Log output section
        log_label = ttk.Label(
            self.analyze_frame,
            text="Log Output:",
            font=("Segoe UI", 11, "bold")
        )
        log_label.grid(row=6, column=0, sticky="nw", pady=(10, 5))

        log_frame = ttk.Frame(self.analyze_frame)
        log_frame.grid(row=7, column=0, sticky="nsew", pady=5)
        log_frame.grid_rowconfigure(0, weight=1)
        log_frame.grid_columnconfigure(0, weight=1)

        self.log_text = tk.Text(log_frame, height=8, width=50, state="disabled", wrap="word")
        log_scrollbar = ttk.Scrollbar(log_frame, orient="vertical", command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)

        self.log_text.grid(row=0, column=0, sticky="nsew")
        log_scrollbar.grid(row=0, column=1, sticky="ns")

    # MARK: Credential Methods
    def _load_existing_credentials(self) -> None:
        """Load existing credentials from .env file."""
        load_dotenv()

        refresh_token = os.getenv("SP_API_REFRESH_TOKEN", "")
        client_id = os.getenv("SP_API_CLIENT_ID", "")
        client_secret = os.getenv("SP_API_CLIENT_SECRET", "")

        self.refresh_token_var.set(refresh_token)
        self.client_id_var.set(client_id)
        self.client_secret_var.set(client_secret)

        if refresh_token and client_id and client_secret:
            self.credentials_status_var.set("Status: Credentials loaded from .env")
            self._set_status_color("green")
        else:
            self.credentials_status_var.set("Status: Credentials not configured")
            self._set_status_color("gray")

    def _toggle_credential_visibility(self) -> None:
        """Toggle visibility of credential fields."""
        show_char = "" if self.show_credentials_var.get() else "*"
        self.refresh_token_entry.configure(show=show_char)
        self.client_secret_entry.configure(show=show_char)

    def _set_status_color(self, color: str) -> None:
        """Set the credentials status label color."""
        self.credentials_status.configure(foreground=color)

    def test_connection(self) -> None:
        """Test SP-API connection with current credentials."""
        refresh_token = self.refresh_token_var.get().strip()
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()

        if not all([refresh_token, client_id, client_secret]):
            self.credentials_status_var.set("Status: Please fill in all credential fields")
            self._set_status_color("red")
            return

        self.credentials_status_var.set("Status: Testing connection...")
        self._set_status_color("orange")
        self.test_btn.configure(state="disabled")
        self.root.update()

        # Configure API with current credentials
        self.analyzer.api.configure(refresh_token, client_id, client_secret)

        # Test in background thread
        def test_worker() -> None:
            try:
                success = self.analyzer.api.test_connection()
                self.root.after(0, self._handle_test_result, success)
            except Exception as ex:
                error_msg = str(ex)
                self.root.after(0, self._handle_test_result, False, error_msg)

        thread = threading.Thread(target=test_worker, daemon=True)
        thread.start()

    def _handle_test_result(self, success: bool, error: str = "") -> None:
        """Handle the result of connection test."""
        self.test_btn.configure(state="normal")

        if success:
            self.credentials_status_var.set("Status: Connection successful!")
            self._set_status_color("green")
        else:
            msg = f"Status: Connection failed - {error}" if error else "Status: Connection failed"
            self.credentials_status_var.set(msg)
            self._set_status_color("red")

    def save_credentials(self) -> None:
        """Save credentials to .env file."""
        refresh_token = self.refresh_token_var.get().strip()
        client_id = self.client_id_var.get().strip()
        client_secret = self.client_secret_var.get().strip()

        if not all([refresh_token, client_id, client_secret]):
            messagebox.showwarning("Warning", "Please fill in all credential fields")
            return

        try:
            self.analyzer.file.update_env_file({
                "SP_API_REFRESH_TOKEN": refresh_token,
                "SP_API_CLIENT_ID": client_id,
                "SP_API_CLIENT_SECRET": client_secret,
                "SP_API_MARKETPLACE_ID": "ATVPDKIKX0DER"
            })

            # Reload environment
            load_dotenv(override=True)

            # Update API credentials
            self.analyzer.api.configure(refresh_token, client_id, client_secret)

            self.credentials_status_var.set("Status: Credentials saved to .env")
            self._set_status_color("green")
            messagebox.showinfo("Success", "Credentials saved successfully!")

        except Exception as e:
            self.logger.error(f"Failed to save credentials: {e}")
            messagebox.showerror("Error", f"Failed to save credentials: {e}")

    # MARK: Analysis Methods
    def _update_asin_count(self, event=None) -> None:
        """Update the ASIN count label."""
        asins = self._get_asins()
        self.asin_count_var.set(f"ASINs to analyze: {len(asins)}")

    def _clear_asins(self) -> None:
        """Clear the ASIN text area."""
        self.asin_text.delete("1.0", tk.END)
        self._update_asin_count()

    def _browse_output(self) -> None:
        """Open file browser for output file selection."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
            initialfile=self.output_path_var.get()
        )
        if filepath:
            self.output_path_var.set(filepath)

    def _get_asins(self) -> List[str]:
        """
        Parse and validate ASINs from text area.

        Returns
        -------
        List[str]
            List of valid ASINs
        """
        text = self.asin_text.get("1.0", tk.END)
        lines = text.strip().split("\n")

        asins = []
        asin_pattern = re.compile(r"^[A-Z0-9]{10}$")

        for line in lines:
            asin = line.strip().upper()
            if asin and asin_pattern.match(asin):
                asins.append(asin)

        return list(set(asins))  # Remove duplicates

    def _log_message(self, message: str) -> None:
        """
        Add message to log output.

        Parameters
        ----------
        message : str
            Message to log
        """
        self.log_text.configure(state="normal")
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.configure(state="disabled")

    def start_analysis(self) -> None:
        """Start Buy Box analysis in background thread."""
        if self.is_analyzing:
            messagebox.showwarning("Warning", "Analysis already in progress")
            return

        # Get and validate ASINs
        asins = self._get_asins()
        if not asins:
            messagebox.showwarning("Warning", "Please enter at least one valid ASIN")
            return

        # Check credentials
        if not self.analyzer.api.credentials:
            messagebox.showwarning(
                "Warning",
                "Please configure SP-API credentials first"
            )
            self.notebook.select(0)  # Switch to credentials tab
            return

        # Get output path
        output_path = self.output_path_var.get().strip()
        if not output_path:
            output_path = self.analyzer.file.get_default_output_path()
            self.output_path_var.set(output_path)

        # Clear log and reset progress
        self.log_text.configure(state="normal")
        self.log_text.delete("1.0", tk.END)
        self.log_text.configure(state="disabled")
        self.progress_var.set(0)

        # Disable UI
        self.is_analyzing = True
        self.analyze_btn.configure(state="disabled")
        self.asin_text.configure(state="disabled")

        self._log_message(f"Starting analysis for {len(asins)} ASINs...")

        # Set up progress callback
        self.analyzer.set_progress_callback(self._progress_callback)

        # Start analysis thread
        self.analysis_thread = threading.Thread(
            target=self._analysis_worker,
            args=(asins, output_path),
            daemon=True
        )
        self.analysis_thread.start()

    def _progress_callback(self, current: int, total: int, message: str) -> None:
        """Handle progress updates from analyzer."""
        self.root.after(0, self._update_progress, current, total, message)

    def _update_progress(self, current: int, total: int, message: str) -> None:
        """Update progress bar and status (thread-safe)."""
        percentage = (current / total) * 100 if total > 0 else 0
        self.progress_var.set(percentage)
        self.analysis_status_var.set(f"{message} ({current}/{total})")
        self._log_message(message)

    def _analysis_worker(self, asins: List[str], output_path: str) -> None:
        """Background worker for analysis."""
        try:
            result = self.analyzer.run(asins, output_path)
            self.root.after(0, self._analysis_complete, result)
        except Exception as ex:
            error_msg = str(ex)
            self.root.after(0, self._analysis_failed, error_msg)

    def _analysis_complete(self, result: dict) -> None:
        """Handle successful analysis completion."""
        self.is_analyzing = False
        self.analyze_btn.configure(state="normal")
        self.asin_text.configure(state="normal")
        self.progress_var.set(100)

        success_count = result.get("success_count", 0)
        error_count = result.get("error_count", 0)
        output_path = result.get("output_path", "")

        self.analysis_status_var.set("Analysis complete!")
        self._log_message(f"Analysis complete: {success_count} successful, {error_count} errors")
        self._log_message(f"Results saved to: {output_path}")

        # Ask to open file
        if messagebox.askyesno(
            "Analysis Complete",
            f"Analysis complete!\n\n"
            f"Successful: {success_count}\n"
            f"Errors: {error_count}\n\n"
            f"Would you like to open the results file?"
        ):
            try:
                os.startfile(output_path)
            except Exception as e:
                self.logger.warning(f"Could not open file: {e}")

    def _analysis_failed(self, error: str) -> None:
        """Handle analysis failure."""
        self.is_analyzing = False
        self.analyze_btn.configure(state="normal")
        self.asin_text.configure(state="normal")

        self.analysis_status_var.set("Analysis failed")
        self._log_message(f"Error: {error}")

        messagebox.showerror("Error", f"Analysis failed: {error}")

    # MARK: Main Loop
    def run(self) -> None:
        """Start the GUI main loop."""
        self.logger.info("Starting GUI main loop")
        self.root.mainloop()

    def dispose(self) -> None:
        """Clean up resources."""
        self.logger.info("Disposing of Tool class")
        if hasattr(self, "analyzer") and self.analyzer:
            self.analyzer.dispose()


if __name__ == "__main__":
    tool = Tool()
    try:
        tool.run()
    finally:
        tool.dispose()
