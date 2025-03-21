import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import os
import shutil
import io

class GuardianProApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Guardian Pro - Child Protection System")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        # Set app icon if available
        try:
            self.root.iconbitmap("guardian_icon.ico")
        except:
            pass
        
        # Variables
        self.selected_image_path = None
        self.processed_image = None
        
        # Create main frame
        self.main_frame = tk.Frame(root, bg="#f0f0f0")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # App title
        title_label = tk.Label(
            self.main_frame, 
            text="Guardian Pro", 
            font=("Arial", 24, "bold"),
            bg="#f0f0f0",
            fg="#2c3e50"
        )
        title_label.pack(pady=(0, 10))
        
        subtitle_label = tk.Label(
            self.main_frame, 
            text="Comprehensive Child Protection System",
            font=("Arial", 14),
            bg="#f0f0f0",
            fg="#34495e"
        )
        subtitle_label.pack(pady=(0, 20))
        
        # Image frame
        self.image_frame = tk.Frame(self.main_frame, bg="#ffffff", bd=2, relief=tk.GROOVE)
        self.image_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.image_label = tk.Label(
            self.image_frame,
            text="No image selected. Upload an image to analyze.",
            bg="#ffffff",
            font=("Arial", 12)
        )
        self.image_label.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Buttons frame
        button_frame = tk.Frame(self.main_frame, bg="#f0f0f0")
        button_frame.pack(fill=tk.X, pady=20)
        
        # Upload button
        self.upload_button = tk.Button(
            button_frame,
            text="Upload Image",
            command=self.upload_image,
            font=("Arial", 12),
            bg="#3498db",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8
        )
        self.upload_button.pack(side=tk.LEFT, padx=(0, 10))
        
        # Process button
        self.process_button = tk.Button(
            button_frame,
            text="Analyze Image",
            command=self.process_image,
            font=("Arial", 12),
            bg="#2ecc71",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            state=tk.DISABLED
        )
        self.process_button.pack(side=tk.LEFT, padx=10)
        
        # Download button
        self.download_button = tk.Button(
            button_frame,
            text="Download Report",
            command=self.download_report,
            font=("Arial", 12),
            bg="#9b59b6",
            fg="white",
            relief=tk.FLAT,
            padx=15,
            pady=8,
            state=tk.DISABLED
        )
        self.download_button.pack(side=tk.LEFT, padx=10)

    def upload_image(self):
        """Allow user to select an image file"""
        file_path = filedialog.askopenfilename(
            title="Select Image",
            filetypes=(
                ("Image files", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("All files", "*.*")
            )
        )
        
        if file_path:
            self.selected_image_path = file_path
            self.display_image(file_path)
            self.process_button.config(state=tk.NORMAL)
            
    def display_image(self, image_path):
        """Display the selected image"""
        try:
            # Load and resize image for display
            img = Image.open(image_path)
            img = self.resize_image(img, (400, 300))
            
            photo_img = ImageTk.PhotoImage(img)
            
            # Update image label
            self.image_label.config(image=photo_img, text="")
            self.image_label.image = photo_img  # Keep reference
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load image: {e}")
    
    def resize_image(self, img, size):
        """Resize image while maintaining aspect ratio"""
        width, height = img.size
        max_width, max_height = size
        
        # Calculate new dimensions
        if width > height:
            new_width = min(width, max_width)
            new_height = int(height * (new_width / width))
        else:
            new_height = min(height, max_height)
            new_width = int(width * (new_height / height))
            
        return img.resize((new_width, new_height), Image.LANCZOS)
    
    def process_image(self):
        """Simulate image analysis for child protection"""
        if not self.selected_image_path:
            messagebox.showwarning("Warning", "Please upload an image first")
            return
            
        # Simulate processing with a simple overlay
        try:
            img = Image.open(self.selected_image_path)
            # Create a processed version (just add a green border for demo)
            width, height = img.size
            bordered_img = Image.new("RGB", (width + 20, height + 20), color=(46, 204, 113))
            bordered_img.paste(img, (10, 10))
            
            # Add a "SAFE" watermark in this demo version
            from PIL import ImageDraw, ImageFont
            draw = ImageDraw.Draw(bordered_img)
            
            # Try to use a system font, fallback to default if not available
            try:
                font = ImageFont.truetype("arial.ttf", 36)
            except:
                font = ImageFont.load_default()
                
            draw.text((width//2, height//2), "SAFE", fill=(255, 255, 255, 128), font=font, anchor="mm")
            
            # Save processed image
            self.processed_image = bordered_img
            
            # Display processed image
            resized = self.resize_image(bordered_img, (400, 300))
            photo_img = ImageTk.PhotoImage(resized)
            self.image_label.config(image=photo_img)
            self.image_label.image = photo_img
            
            # Enable download button
            self.download_button.config(state=tk.NORMAL)
            
            messagebox.showinfo("Analysis Complete", "Image analysis complete. The content appears to be appropriate for children.")
            
        except Exception as e:
            messagebox.showerror("Processing Error", f"Failed to process image: {e}")
    
    def download_report(self):
        """Save the processed image and a sample report"""
        if not self.processed_image:
            messagebox.showwarning("Warning", "No processed image to download")
            return
            
        # Ask for save location
        save_dir = filedialog.askdirectory(title="Select Folder to Save Report")
        
        if not save_dir:
            return
            
        try:
            # Save the processed image
            image_path = os.path.join(save_dir, "guardian_pro_analyzed_image.png")
            self.processed_image.save(image_path)
            
            # Create a simple report
            report_path = os.path.join(save_dir, "guardian_pro_report.txt")
            with open(report_path, "w") as f:
                f.write("Guardian Pro - Image Analysis Report\n")
                f.write("=====================================\n\n")
                f.write(f"Date: {import_time().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Analyzed file: {os.path.basename(self.selected_image_path)}\n\n")
                f.write("Analysis Results:\n")
                f.write("- No inappropriate content detected\n")
                f.write("- Image appears suitable for children\n")
                f.write("- No known harmful elements identified\n\n")
                f.write("Recommendation: This image is safe for children's viewing.\n\n")
                f.write("Note: This is a demonstration report. A full Guardian Pro analysis would include\n")
                f.write("detailed AI-based content assessment and age-appropriate recommendations.\n")
            
            messagebox.showinfo("Download Complete", 
                                f"Report and analyzed image have been saved to:\n{save_dir}")
            
        except Exception as e:
            messagebox.showerror("Download Error", f"Failed to save report: {e}")

# Helper function for time (defined separately to avoid issues)
def import_time():
    import datetime
    return datetime

# Run the application
if __name__ == "__main__":
    root = tk.Tk()
    app = GuardianProApp(root)
    root.mainloop()