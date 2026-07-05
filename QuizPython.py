import tkinter as tk
from tkinter import ttk

root = tk.Tk()
root.title("Bio Data Form")

form_frame = tk.Frame(root, padx=20, pady=20, bg="#E6F0FF", bd=25)
form_frame.pack(padx=30, pady=30)


title_label = tk.Label(form_frame, text="Bio Data Form", font=("Arial", 16, "bold"), bg="#E6F0FF")
title_label.grid(row=0, column=0, columnspan=2, pady=(0, 15))


name_label = tk.Label(form_frame, text="Full Name:", bg="#E6F0FF")
name_label.grid(row=1, column=0, pady=5)
name_entry = tk.Entry(form_frame, width=30)
name_entry.grid(row=1, column=1, pady=5)

gender_label = tk.Label(form_frame, text="Gender:", bg="#E6F0FF")
gender_label.grid(row=2, column=0, sticky="w", pady=5)

gender_var = tk.StringVar(value="Male")
male_radio = tk.Radiobutton(form_frame, text="Male", variable=gender_var, value="Male", bg="#E6F0FF")
male_radio.grid(row=2, column=1, sticky="w", padx=(0, 50))
female_radio = tk.Radiobutton(form_frame, text="Female", variable=gender_var, value="Female", bg="#E6F0FF")
female_radio.grid(row=2, column=1, sticky="e", padx=(0, 5))

age_label = tk.Label(form_frame, text="Age:", bg="#E6F0FF")
age_label.grid(row=3, column=0, sticky="w", pady=5)

ages = [str(i) for i in range(0 ,20)]
age_var = tk.StringVar(value=ages[0])
age_dropdown = ttk.Combobox(form_frame, textvariable=age_var, values=ages, state="readonly", width=5)
age_dropdown.grid(row=3, column=1, sticky="w", pady=5)

hobbies_label = tk.Label(form_frame, text="Hobbies:", bg="#E6F0FF")
hobbies_label.grid(row=4, column=0, sticky="nw", pady=5)

hobbies_frame = tk.Frame(form_frame, bg="#E6F0FF")
hobbies_frame.grid(row=4, column=1, sticky="w")

reading_var = tk.BooleanVar(value=True)
sports_var = tk.BooleanVar(value=True)
music_var = tk.BooleanVar(value=False)

reading_check = tk.Checkbutton(hobbies_frame, text="Reading", variable=reading_var, bg="#E6F0FF")
reading_check.pack(anchor="w")
sports_check = tk.Checkbutton(hobbies_frame, text="Sports", variable=sports_var, bg="#E6F0FF")
sports_check.pack(anchor="w")
music_check = tk.Checkbutton(hobbies_frame, text="Music", variable=music_var, bg="#E6F0FF")
music_check.pack(anchor="w")

submit_button = tk.Button(form_frame, text="Submit", bg="#4CAF50", fg="white", font=("Arial", 10, "bold"))
submit_button.grid(row=5, column=0, columnspan=2, pady=20)


root.mainloop()