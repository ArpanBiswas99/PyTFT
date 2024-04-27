#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jul  3 20:04:22 2023

@author: abiswas
"""

import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import configparser
import threading
import os
import sys
from tkinter import Tk

from tkinter import font as tkfont
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from ttkthemes import ThemedTk
from ttkthemes import ThemedStyle

from PIL import Image, ImageTk

import matplotlib.pyplot as plt
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

import subprocess
from scipy.optimize import minimize,differential_evolution,curve_fit,least_squares,basinhopping
from random import random, randint
import random

import re

from matplotlib.backends.backend_pdf import PdfPages


class GUI(ThemedTk):
    def __init__(self, *args, **kwargs):
        ThemedTk.__init__(self, *args, **kwargs)
        self.get_themes() 
        self.set_theme("ubuntu")  

        self.title("TFT Parameter Extraction")
        
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TLabelframe.Label', font=("Arial", 14, "bold"))
        
    
        # Get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        # Set the window size to the screen resolution
        self.geometry(f'{screen_width}x{screen_height}')
    
        # Load config file
        self.config_parser = configparser.ConfigParser()
        self.config_parser.read("config.ini")
    
        # Input and output file paths
        self.input_file = tk.StringVar()
        self.output_file = tk.StringVar()
    
        # Optimization algorithm
        self.algorithm_var = tk.StringVar()
        self.algorithm_var.set("Differential Evolution")
    
        # Create GUI elements
        self.create_menu()
        self.create_file_selection_frame()
        self.create_output_parameters_frame()
        self.create_mosfet_parameters_frame()
    
        # Initialize plot canvases
        self.plot_canvases = []
    
        # Create output graphs frame
        self.create_output_graphs_frame()
    
        # Create run button
        self.create_run_button()
    
        # Load file paths from config
        self.input_file.set(self.config_parser.get("Files", "input_file", fallback=""))
        self.output_file.set(self.config_parser.get("Files", "output_file", fallback=""))
    
        # Load parameters
        self.load_parameters()
    
        self.thread = None
        
    def on_close(self):
        # Stop the thread execution
        self.save_parameters()
        if self.thread and self.thread.is_alive():
            if not self.thread.is_alive():
                self.thread.daemon = True
                self.thread.join()
    
        # Close the GUI
        self.destroy()
    
    def create_menu(self):
        menu_bar = tk.Menu(self)
        menu_bar.configure(bg="white")

        # File menu
        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Open Input File", command=self.browse_input_file)
        file_menu.add_command(label="Open Output File", command=self.browse_output_file)
        file_menu.add_separator()
        file_menu.add_command(label="Save Output Parameters", command=self.save_output_parameters)
        file_menu.add_command(label="Save Plots as PDF", command=self.save_plots_as_pdf)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.on_close)
        menu_bar.add_cascade(label="File", menu=file_menu)

        # Algorithm menu
        algorithm_menu = tk.Menu(menu_bar, tearoff=0)
        algorithm_menu.add_radiobutton(label="Differential Evolution",
                                       variable=self.algorithm_var,
                                       value="Differential Evolution",
                                       command=self.algorithm_changed)
        algorithm_menu.add_radiobutton(label="Differential Evolution Custom",
                                       variable=self.algorithm_var,
                                       value="Differential Evolution Custom",
                                       command=self.algorithm_changed)
        menu_bar.add_cascade(label="Algorithm", menu=algorithm_menu)
        
        # Load saved parameters from configuration file
        self.load_parameters()

        # Run menu
        run_menu = tk.Menu(menu_bar, tearoff=0)
        run_menu.add_command(label="Run", command=self.run_algorithm)
        menu_bar.add_cascade(label="Run", menu=run_menu)
     
        
        # About menu
        about_menu = tk.Menu(menu_bar, tearoff=0)
        about_menu.add_command(label="About", command=self.open_about_window)
        menu_bar.add_cascade(label="About", menu=about_menu)
        
        # Help menu
        help_menu = tk.Menu(menu_bar, tearoff=0)
        help_menu.add_command(label="How to Use", command=self.open_help_window)
        menu_bar.add_cascade(label="Help", menu=help_menu)
        
        self.config(menu=menu_bar)
        
    def open_about_window(self):
        about_window = tk.Toplevel(self)
        about_window.title("About")
        about_window.configure(bg="white")

        about_text = """
        Program Name: IGZO TFT Parameter Extraction
        Version: 1.3
        Change-log: Added model parameter clipboard
        Author: Arpan Biswas, Patrick Schalberger
        
        Institute: Institut für Großflächige Mikroelektronik (IGM)
        University: Universität Stuttgart

        This program performs parameter extraction for IGZO TFT (Thin-Film Transistor) devices. It uses differential evolution optimization algorithm to find the optimal parameter values based on the provided input and output data files.
        """

        about_label = tk.Label(about_window, text=about_text, padx=10, pady=10, bg='white')
        about_label.pack() 

        
    def open_help_window(self):
        help_window = tk.Toplevel(self)
        help_window.title("Help")
        help_window.configure(bg="white")
    
        help_text = """
        How to Use IGZO TFT Parameter Extraction Program:
        
        1. Open Input File:
            - Click on 'File' -> 'Open Input File' menu item.
            - Select the input data file (.dat) containing the measured input characteristics of the IGZO TFT device.
            - This also automatically selects the corresponding output file so no need to select output file again.
        
        2. Open Output File:
            - Click on 'File' -> 'Open Output File' menu item.
            - Select the output data file (.dat) containing the measured output characteristics of the IGZO TFT device.
        
        3. Configure Algorithm (Optional):
            - Click on 'Algorithm' menu item.
            - Choose the desired optimization algorithm for parameter extraction.
        
        4. Run Parameter Extraction:
            - Click on 'Run' -> 'Run' menu item.
            - The program will extract the parameters using the selected algorithm and display the results.
        
        5. Save Output Parameters:
            - Click on 'File' -> 'Save Output Parameters' menu item.
            - Choose the location to save the extracted parameter values as a text file (.txt).
        
        6. Save Plots as PDF (Optional):
            - Click on 'File' -> 'Save Plots as PDF' menu item.
            - Choose the location to save the generated plots as a PDF file (.pdf).
        
        Differential Evolution Custom:
            - This algorithm is a customized version of the Differential Evolution algorithm for parameter extraction.
            - It allows you to specify custom settings for the algorithm parameters.
        
        Parameters for Differential Evolution Custom:
            - Population Size: The number of individuals in each generation of the algorithm.
            - Mutation Factor (F): The scaling factor for the difference vector used in mutation.
            - Crossover Probability (CR): The probability of recombination between the target vector and the mutant vector.
            - Maximum Generations: The maximum number of generations for the algorithm to converge.
        
        Output Parameters:
            - The program will display the final predicted values for the following parameters:
            - Threshold Voltage (VTO)
            - Mobility (U0)
            - Output resistance coefficient (Kappa)
            - Static feedback factor for adjusting threshold (Eta)
            - Channel length modulation (LAMBDA)
            - Bulk charge effect parameter (nfs)
            - Bulk surface doping (nsub)
            - Mobility degradation factor (Theta)
            - These parameters represent the extracted characteristics of the IGZO TFT device.
        
        """
    
        help_label = tk.Label(help_window, text=help_text, padx=10, pady=10, justify='left')
        help_label.pack()


       

    def algorithm_changed(self, event=None):
        selected_algorithm = self.algorithm_var.get()
        if selected_algorithm == "Differential Evolution":
            self.algorithm_combo.set("Differential Evolution")
            self.iterations_entry.configure(state=tk.NORMAL)
            self.population_size_entry.configure(state=tk.DISABLED)
            self.mutation_factor_entry.configure(state=tk.DISABLED)
            self.crossover_prob_entry.configure(state=tk.DISABLED)
        elif selected_algorithm == "Differential Evolution Custom":
            self.algorithm_combo.set("Differential Evolution Custom")
            self.iterations_entry.configure(state=tk.NORMAL)
            self.population_size_entry.configure(state=tk.NORMAL)
            self.mutation_factor_entry.configure(state=tk.NORMAL)
            self.crossover_prob_entry.configure(state=tk.NORMAL)
            
    def load_parameters(self):
        config = configparser.ConfigParser()
        config.read('config_parameters.ini')

        if 'Algorithm' in config:
            selected_algorithm = config['Algorithm'].get('SelectedAlgorithm')
            if selected_algorithm:
                self.algorithm_var.set(selected_algorithm)


    def create_file_selection_frame(self):
        file_selection_frame = ttk.LabelFrame(self, text="File Selection",  style="Bold.TLabelframe")
        file_selection_frame.grid(row=0, column=0, columnspan = 2, padx=10, pady=10, sticky="nsew")
        #self.columnconfigure(0, weight=1)

        input_label = ttk.Label(file_selection_frame, text="Input File")
        input_label.grid(row=0, column=0, padx=10)

        input_entry = ttk.Entry(file_selection_frame, textvariable=self.input_file, width=100)
        input_entry.grid(row=0, column=1, padx=10)

        input_button = ttk.Button(file_selection_frame, text="Browse", command=self.browse_input_file)
        input_button.grid(row=0, column=2, padx=10)

        output_label = ttk.Label(file_selection_frame, text="Output File")
        output_label.grid(row=1, column=0, padx=10)

        output_entry = ttk.Entry(file_selection_frame, textvariable=self.output_file, width=100)
        output_entry.grid(row=1, column=1, padx=10)

        output_button = ttk.Button(file_selection_frame, text="Browse", command=self.browse_output_file)
        output_button.grid(row=1, column=2, padx=10)
        
        # Update MOSFET parameters frame after file selection
        def update_mosfet_parameters_frame():
            self.create_mosfet_parameters_frame()
        
        self.input_file.trace("w", lambda *args: update_mosfet_parameters_frame())
        self.output_file.trace("w", lambda *args: update_mosfet_parameters_frame())
        
    def create_mosfet_parameters_frame(self):
        mosfet_params_frame = ttk.LabelFrame(self, text="MOSFET Parameters", style="Bold.TLabelframe")
        mosfet_params_frame.grid(row=1, column=0, pady=10, padx=10, sticky="nsew")
    
        # Create and place the frame widgets
        t_ox_label = ttk.Label(mosfet_params_frame, text="Thickness of oxide layer (t_ox) in nm:")
        t_ox_label.grid(row=0, column=0, padx=10, pady=5)
    
        self.t_ox_entry = ttk.Entry(mosfet_params_frame)
        self.t_ox_entry.grid(row=0, column=1, padx=10, pady=5)
        self.t_ox_entry.insert(0, "65")  # Default value for t_ox
    
        kappa_label = ttk.Label(mosfet_params_frame, text="Dielectric constant of SiO2 (kappa):")
        kappa_label.grid(row=1, column=0, padx=10, pady=5)
    
        self.kappa_entry = ttk.Entry(mosfet_params_frame)
        self.kappa_entry.grid(row=1, column=1, padx=10, pady=5)
        self.kappa_entry.insert(0, "3.9")  # Default value for kappa
    
        additional_params_frame = ttk.Frame(mosfet_params_frame)
        additional_params_frame.grid(row=2, column=0, columnspan=2, pady=10)
    
        def calculate_additional_params():
            def read_dimensions(input_filename):
                parameters = {}
                
                # Read the input data
                with open(input_filename, "r", encoding='ISO-8859-1') as file:
                    lines = file.readlines()
                    for line in lines:
                        if line.startswith("-") or line[0].isdigit():
                            data = list(map(float, line.strip().split()))
                        else:
                            # Attempt to parse parameter
                            parts = line.split(':')
                            if len(parts) == 2:
                                key = parts[0].strip()
                                try:
                                    value = float(parts[1].strip())
                                except ValueError:
                                    value = parts[1].strip()  # keep as string if it's not a number
                                parameters[key] = value
            
                ch_length = parameters.get('Ch_length', 0)
                ch_width = parameters.get('Ch_width', 0)
                ch_height = parameters.get('Ch_height', 0)
                Epsilon_r = parameters.get('Epsilon_r', 0)

                # Return the input and output data as NumPy arrays along with Ug_output
                return ch_width, ch_length, ch_height, Epsilon_r
            
            unknown_input_file = self.input_file.get()
            if unknown_input_file != '':      
                ch_width, ch_length, ch_height, Epsilon_r = read_dimensions(unknown_input_file)    
            else:
                ch_width, ch_length, ch_height, Epsilon_r = 0, 0, 65e-9, 4
    
            # Device dimensions and thicknesses
            W = ch_width
            width = int(W/(1e-6)) #um
            L = ch_length
            length = int(L/(1e-6)) #um
            t_dielectric = ch_height
            t_dielectric1 = str(t_dielectric/(1e-9))
            self.t_ox_entry.delete(0, tk.END)
            self.t_ox_entry.insert(0, t_dielectric1)

            # Dielectric constant of SiO2
            kappa = Epsilon_r
            kappa1 = str(Epsilon_r)
            self.kappa_entry.delete(0, tk.END)
            self.kappa_entry.insert(0, kappa1)
    
            # Constants
            epsilon_0 = 8.854e-12  # F/m
    
            # Calculating the oxide capacitance per unit area
            epsilon_ox = kappa * epsilon_0
            C_ox = epsilon_ox / t_dielectric
    
            param_labels = [
                ("Width x Length (um x um):", f"{width} um x {length} um"),
                ("epsilon_0:", f"{epsilon_0:.2e} F/m"),
                ("C_ox:", f"{C_ox:.2e} F/m^2"),
            ]
    
            # Clear previous labels
            for widget in additional_params_frame.winfo_children():
                widget.destroy()
    
            # Display the additional parameters
            for i, (param_label, param_value) in enumerate(param_labels):
                label = ttk.Label(additional_params_frame, text=param_label)
                label.grid(row=i, column=0, padx=10, sticky="e")
    
                value = ttk.Label(additional_params_frame, text=param_value, anchor="w")
                value.grid(row=i, column=1, padx=10, sticky="w")
    
        # Calculate and display additional parameters when the entries are modified
        self.t_ox_entry.bind("<FocusOut>", lambda event: calculate_additional_params())
        self.kappa_entry.bind("<FocusOut>", lambda event: calculate_additional_params())
    
        # Calculate and display additional parameters initially
        calculate_additional_params()


    def create_run_button(self):
        run_frame = ttk.LabelFrame(self, text="Optimzation Algorithm",  style="Bold.TLabelframe")
        run_frame.grid(row=1, column=1, pady=10, padx=10, sticky="nsew")
        #self.columnconfigure(0, weight=1)
        #self.columnconfigure(1, weight=1)
    
        algorithm_label = ttk.Label(run_frame, text="Optimization Algorithm:")
        algorithm_label.grid(row=0, column=0, padx=10)
    
        self.algorithm_combo = ttk.Combobox(run_frame, values=["Differential Evolution", "Differential Evolution Custom"], width=50)
        self.algorithm_combo.grid(row=0, column=1, padx=10)
        self.algorithm_combo.current(0)  # Set the default algorithm
    
        # Parameters for Differential Evolution
        de_params_frame = ttk.Frame(run_frame)
        de_params_frame.grid(row=1, column=0, columnspan=3, pady=10)
    
        iterations_label = ttk.Label(de_params_frame, text="Number of Iterations:")
        iterations_label.grid(row=0, column=0, padx=10)
    
        self.iterations_entry = ttk.Entry(de_params_frame)
        self.iterations_entry.grid(row=0, column=1, padx=10)
        self.iterations_entry.insert(0, "10")  # Set a default value
    
        population_size_label = ttk.Label(de_params_frame, text="Population Size:")
        population_size_label.grid(row=1, column=0, padx=10)
    
        self.population_size_entry = ttk.Entry(de_params_frame)
        self.population_size_entry.grid(row=1, column=1, padx=10)
        self.population_size_entry.insert(0, "50")  # Set a default value
    
        mutation_factor_label = ttk.Label(de_params_frame, text="Mutation Factor:")
        mutation_factor_label.grid(row=2, column=0, padx=10)
    
        self.mutation_factor_entry = ttk.Entry(de_params_frame)
        self.mutation_factor_entry.grid(row=2, column=1, padx=10)
        self.mutation_factor_entry.insert(0, "0.5")  # Set a default value
    
        crossover_prob_label = ttk.Label(de_params_frame, text="Crossover Probability:")
        crossover_prob_label.grid(row=3, column=0, padx=10)
    
        self.crossover_prob_entry = ttk.Entry(de_params_frame)
        self.crossover_prob_entry.grid(row=3, column=1, padx=10)
        self.crossover_prob_entry.insert(0, "0.7")  # Set a default value
        
        def load_parameters():
            config = configparser.ConfigParser()
            config.read('config_parameters.ini')
    
            if 'Algorithm' in config:
                selected_algorithm = config['Algorithm'].get('SelectedAlgorithm')
                if selected_algorithm:
                    self.algorithm_combo.set(selected_algorithm)
    
            if 'Parameters' in config:
                parameters = config['Parameters']
                if 'Iterations' in parameters:
                    self.iterations_entry.delete(0, tk.END)
                    self.iterations_entry.insert(0, parameters['Iterations'])
    
                if 'PopulationSize' in parameters:
                    self.population_size_entry.delete(0, tk.END)
                    self.population_size_entry.insert(0, parameters['PopulationSize'])
    
                if 'MutationFactor' in parameters:
                    self.mutation_factor_entry.delete(0, tk.END)
                    self.mutation_factor_entry.insert(0, parameters['MutationFactor'])
    
                if 'CrossoverProbability' in parameters:
                    self.crossover_prob_entry.delete(0, tk.END)
                    self.crossover_prob_entry.insert(0, parameters['CrossoverProbability'])
    
        # Load saved parameters from configuration file
        load_parameters()
        
        def algorithm_changed(*args):
            selected_algorithm = self.algorithm_combo.get()
            if selected_algorithm == "Differential Evolution":
                self.algorithm_var.set("Differential Evolution")
                self.iterations_entry.configure(state=tk.NORMAL)
                self.population_size_entry.configure(state=tk.DISABLED)
                self.mutation_factor_entry.configure(state=tk.DISABLED)
                self.crossover_prob_entry.configure(state=tk.DISABLED)
            elif selected_algorithm == "Differential Evolution Custom":
                self.algorithm_var.set("Differential Evolution Custom")
                self.iterations_entry.configure(state=tk.NORMAL)
                self.population_size_entry.configure(state=tk.NORMAL)
                self.mutation_factor_entry.configure(state=tk.NORMAL)
                self.crossover_prob_entry.configure(state=tk.NORMAL)
        
        self.algorithm_combo.bind("<<ComboboxSelected>>", algorithm_changed)
        algorithm_changed()  # Call the function initially to set the correct initial state
        
        run_button = ttk.Button(run_frame, text="Run", command=self.run_algorithm)
        run_button.grid(row=0, column=2, padx=10, pady=10)


        # Save parameters whenever they are changed
        self.iterations_entry.bind("<FocusOut>", self.save_parameters)
        self.population_size_entry.bind("<FocusOut>", self.save_parameters)
        self.mutation_factor_entry.bind("<FocusOut>", self.save_parameters)
        self.crossover_prob_entry.bind("<FocusOut>", self.save_parameters)
        
    def save_parameters(self, *args):
        config = configparser.ConfigParser()

        selected_algorithm = self.algorithm_combo.get()
        config['Algorithm'] = {'SelectedAlgorithm': selected_algorithm}

        if selected_algorithm == "Differential Evolution":
            config['Parameters'] = {
                'Iterations': self.iterations_entry.get(),
                'PopulationSize': self.population_size_entry.get(),
                'MutationFactor': self.mutation_factor_entry.get(),
                'CrossoverProbability': self.crossover_prob_entry.get()
            }
        elif selected_algorithm == "Differential Evolution Custom":
            config['Parameters'] = {
                'Iterations': self.iterations_entry.get(),
                'PopulationSize': self.population_size_entry.get(),
                'MutationFactor': self.mutation_factor_entry.get(),
                'CrossoverProbability': self.crossover_prob_entry.get()
            }

        with open('config_parameters.ini', 'w') as configfile:
            config.write(configfile)


    
    def create_output_parameters_frame(self):
        output_parameters_frame = ttk.LabelFrame(self, text="Output Predicted Parameters", style="Bold.TLabelframe")
        output_parameters_frame.grid(row=0, column=2, rowspan=2, columnspan=1, padx=10, pady=10, sticky="nsew")
        
        self.columnconfigure(1, weight=2)
    
        self.output_parameters_text = tk.Text(output_parameters_frame, height=10, width=100)
        self.output_parameters_text.pack(padx=10, pady=10)

        # Add new button
        self.button = ttk.Button(output_parameters_frame, text="Copy Model Parameter Set", command=self.copy_model_parameters)
        self.button.pack(padx=10, pady=10)
    
    def copy_model_parameters(self):
        try:
            # Read the "input.cir" file
            with open("input.cir", "r") as file:
                # read line by line till we find the .model section
                line = file.readline()
                while line and ".model" not in line:
                    line = file.readline()
    
                # Once the .model section is found, keep reading and collecting the parameter values until "+lambda"
                params = {'u0': None, 'vto': None, 'eta': None, 'nfs': None, 'nsub': None, 'kappa': None, 'theta': None, 'lambda': None}
                while line and "+lambda" not in line:
                    if '=' in line:
                        param, value = line.split('=')[0].strip()[1:], line.split('=')[1].strip().split(' ')[0]
                        if param in params:
                            params[param] = value
                    line = file.readline()
                if '+lambda' in line:
                    params['lambda'] = line.split('=')[1].strip()
    
                parameters = """.model testfet nmos level=3 
    +is=0 u0={u0} vto={vto} gamma=0 pb=0 fc=0 tpg=0 tox=65e-9 eta={eta}
    +nfs={nfs} nsub={nsub} kappa={kappa} theta={theta} lambda={lambda}""".format(**params)
                
                # Copy parameters to clipboard
                self.clipboard_clear()
                self.clipboard_append(parameters)
                self.update() # now it stays on the clipboard after the window is closed
                messagebox.showinfo("Info", "Parameters copied to clipboard!")
                
        except FileNotFoundError:
            messagebox.showerror("Error", "File 'input.cir' not found!")
    
    def create_output_graphs_frame(self):
        frame = ttk.LabelFrame(self, text="Output Graphs", style="Bold.TLabelframe")
        frame.grid(row=2, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
    
        # Configure grid column and row weights
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)
    
        canvas = tk.Canvas(frame, width=800, height=800)
        v_scrollbar = ttk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        h_scrollbar = ttk.Scrollbar(frame, orient="horizontal", command=canvas.xview)  # Horizontal scrollbar
        plots_frame = ttk.Frame(canvas)
    
        self.plot_canvases.append(self.create_plot_canvas(plots_frame, 0, 0))
        self.plot_canvases.append(self.create_plot_canvas(plots_frame, 0, 1))
        self.plot_canvases.append(self.create_plot_canvas(plots_frame, 0, 2))
        self.plot_canvases.append(self.create_plot_canvas(plots_frame, 1, 0))
        self.plot_canvases.append(self.create_plot_canvas(plots_frame, 1, 1))
        self.plot_canvases.append(self.create_plot_canvas(plots_frame, 1, 2))
    
        v_scrollbar.pack(side="right", fill="y")
        h_scrollbar.pack(side="bottom", fill="x")
        canvas.pack(side="left", fill="both", expand=True)
        canvas.create_window((0, 0), window=plots_frame, anchor='n')
        canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set, scrollregion=canvas.bbox("all"))
        plots_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        
        self.update()
    
        def _on_mousewheel(event):
            canvas.yview_scroll(-1 * (event.delta // 120), "units")
    
        def _on_shift_mousewheel(event):
            canvas.xview_scroll(-1 * (event.delta // 120), "units")
    
        frame.bind_all("<MouseWheel>", _on_mousewheel)
        frame.bind_all("<Shift-MouseWheel>", _on_shift_mousewheel)


    def create_plot_canvas(self, parent, row, column):
        plot_canvas = tk.Canvas(parent, width=600, height=400, bg="white")
        plot_canvas.grid(row=row, column=column, padx=10, pady=10, sticky="nsew")
        return plot_canvas

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("DAT Files", "*.dat")])
        if file_path:
            self.input_file.set(file_path)
            self.auto_select_output_file(file_path)

    def browse_output_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("DAT Files", "*.dat")])
        if file_path:
            self.output_file.set(file_path)

    def auto_select_output_file(self, input_file):
        # Extract the file name and directory from the input file path
        input_dir, input_file_name = os.path.split(input_file)

        # Create the output file name based on the input file name
        output_file_name = input_file_name.replace("_input.dat", "_output.dat")

        # Create the output file path by joining the directory and output file name
        output_file = os.path.join(input_dir, output_file_name)

        # Set the output file path
        self.output_file.set(output_file)

    def save_output_parameters(self):
        output_parameters = self.output_parameters_text.get(1.0, tk.END)
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(output_parameters)


    def save_plots_as_pdf(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF Files", "*.pdf")])
    
        if file_path:
            with PdfPages(file_path) as pdf:
                for canvas in self.plot_canvases:
                    figure = canvas.fig_agg.figure
                    pdf.savefig(figure)
    
    
    def run_algorithm(self):
        # Clear previous plot canvases
        for plot_canvas in self.plot_canvases:
            plot_canvas.destroy()
    
        self.plot_canvases = []
        
        # Create output graphs frame
        self.create_output_graphs_frame()

        input_file = self.input_file.get()  # Get the string value from StringVar
        output_file = self.output_file.get()  # Get the string value from StringVar
        algorithm = self.algorithm_var.get()
    
        # Check if the 'Files' section exists in the configuration file
        if not self.config_parser.has_section("Files"):
            self.config_parser.add_section("Files")
    
        # Save file paths to config
        self.config_parser.set("Files", "input_file", input_file)
        self.config_parser.set("Files", "output_file", output_file)
    
        # Write the updated configuration to the file
        with open("config.ini", "w") as configfile:
            self.config_parser.write(configfile)
    
        # Clear the output parameters text
        self.output_parameters_text.delete("1.0", tk.END)
    
    
        # Run algorithm in a separate thread to prevent freezing the GUI
        self.thread = threading.Thread(target=self.run_algorithm_thread, args=(input_file, output_file, algorithm))
        self.thread.start()



    def run_algorithm_thread(self, input_file, output_file, algorithm):
        def read_data(input_filename, output_filename, plot=False):
            colors = ["r", "g", "b", "m"]
            labels = ["Udconst = 0.1", "Udconst = 5.1", "Udconst = 10.1", "Udconst = 15.1"]
            Udconst_values = [0.1, 5.1, 10.1, 15.1]
            Ug_output = [0, 4, 8, 12, 16, 20]
            ############################## input ###################################
            # Initialize lists to store the data
            Ug_input_meas = []
            Id_Udconst = [[] for _ in range(4)]
            parameters = {}
            
            # Read the input data
            with open(input_filename, "r", encoding='ISO-8859-1') as file:
                lines = file.readlines()
                for line in lines:
                    if line.startswith("-") or line[0].isdigit():
                        data = list(map(float, line.strip().split()))
                        if len(data) >= 5:  # Make sure the data list has at least 5 elements
                            Ug_input_meas.append(data[0])
                            for i in range(4):
                                Id_Udconst[i].append(data[i + 1])
                    else:
                        # Attempt to parse parameter
                        parts = line.split(':')
                        if len(parts) == 2:
                            key = parts[0].strip()
                            try:
                                value = float(parts[1].strip())
                            except ValueError:
                                value = parts[1].strip()  # keep as string if it's not a number
                            parameters[key] = value
        
            # Convert to a NumPy array
            Ug_input_meas = np.array(Ug_input_meas)
            Id_input_meas = np.array(Id_Udconst)
        
            ch_length = parameters.get('Ch_length', 0)
            ch_width = parameters.get('Ch_width', 0)
            ch_height = parameters.get('Ch_height', 0)
            Epsilon_r = parameters.get('Epsilon_r', 0)


            ############################## output ###################################    
            # Extract Ud and Id values for different Ug values
            Ud_output_meas = []
            Id_output_meas = [[] for _ in range(6)]  # 6 Ug values: 0, 4, 8, 12, 16, 20V
            
            with open(output_filename, "r", encoding='ISO-8859-1') as file:
                raw_data = file.read()
            # Remove comments and split the data into lines
            data_lines = [line for line in raw_data.split('\n')[27:] if not line.startswith('#') and line.strip()]
            for line in data_lines:
                values = list(map(float, line.split()))
                Ud_output_meas.append(values[0])
                for i in range(6):
                    Id_output_meas[i].append(values[i + 1])
            
            # Convert to NumPy arrays
            Ud_output_meas = np.array(Ud_output_meas)
            Id_output_meas = np.array([np.array(ids) for ids in Id_output_meas])
            
            
            if plot:                
                def plot1(canvas):
                    fig, ax = plt.subplots()
                    # Plot the input data                    
                    for j in range(4):
                        ax.plot(Ug_input_meas, Id_input_meas[j], color=colors[j], label=labels[j])
                    
                    ax.set_title("IGZO TFT Input Characteristics")
                    ax.set_xlabel("Ug (V)")
                    ax.set_ylabel("Id (A)")
                    ax.legend(fontsize=8)                

                    canvas.fig_agg = FigureCanvasTkAgg(fig, master=canvas)
                    canvas.fig_agg.draw()
                    canvas.fig_agg.get_tk_widget().pack(side="top", fill="both", expand=True)
                self.after(0, plot1, self.plot_canvases[0])
                
                def plot2(canvas):
                    fig, ax = plt.subplots()
                    # Plot the input data                               
                    for i, ids in enumerate(Id_output_meas):
                        ax.plot(Ud_output_meas, ids, label=f'Ug = {Ug_output[i]}V')
                    
                    ax.set_title("IGZO TFT Output Characteristics")
                    ax.set_xlabel("Ud (V)")
                    ax.set_ylabel("Id (A)")
                    ax.legend(fontsize=8)  


                    canvas.fig_agg = FigureCanvasTkAgg(fig, master=canvas)
                    canvas.fig_agg.draw()
                    canvas.fig_agg.get_tk_widget().pack(side="top", fill="both", expand=True)
                self.after(0, plot2, self.plot_canvases[1])

            # Return the input and output data as NumPy arrays along with Ug_output
            return Ug_input_meas, Id_input_meas, Ud_output_meas, Id_output_meas, Ug_output, ch_width, ch_length, ch_height, Epsilon_r
            
        unknown_input_file = os.path.basename(input_file)
        unknown_output_file = os.path.basename(output_file)


        Ug_input_meas, Id_input_meas, Ud_output_meas, Id_output_meas, Ug_output, ch_width, ch_length, ch_height, Epsilon_r = read_data(input_file, output_file, plot=True)

        # Device dimensions and thicknesses
        W = ch_width
        width = W/(1e-6) #um
        L = ch_length
        length = L/(1e-6) #um
        t_dielectric = float(self.t_ox_entry.get())*1e-9

        # Dielectric constant of SiO2
        kappa = float(self.kappa_entry.get())

        # Constants
        epsilon_0 = 8.854e-12  # F/m

        # Calculating the oxide capacitance per unit area
        epsilon_ox = kappa * epsilon_0
        C_ox = epsilon_ox / t_dielectric

        ################### Vth Calc ################################# 
        def func_vth(Id_data_list, Ug_array, plot=False):
            def plot_data_and_vth(Id_data, color, label, Ug_array):
                # Calculate the square root of Id_data
                sqrt_Id_data = np.sqrt(np.abs(Id_data))

                # Calculate the slope between consecutive points
                slopes = np.diff(sqrt_Id_data) / np.diff(Ug_array)

                # Find the index with the steepest slope
                steepest_slope_index = np.argmax(slopes)

                # Get the point on the curve corresponding to the steepest slope
                point_x = Ug_array[steepest_slope_index]
                point_y = sqrt_Id_data[steepest_slope_index]

                # Extrapolate the tangent line to the x-axis (Id = 0) and find the corresponding Vth
                Vth = point_x - point_y / slopes[steepest_slope_index]
                
                return Vth

            colors = ["r", "g", "b", "m"]
            labels = ["Udconst = 0.1", "Udconst = 5.1", "Udconst = 10.1", "Udconst = 15.1"]

            vth_list = []
            for i in range(1,4):
                vth = plot_data_and_vth(Id_data_list[i], colors[i], labels[i], Ug_array)
                vth_list.append(vth)

            average_vth = np.mean(vth_list)
            Vth = average_vth

            if plot:                
                def plot3(canvas):
                    fig, ax = plt.subplots()
                    # Plot the input data                    
                    for i in range(4):
                        sqrt_Id_data = np.sqrt(np.abs(Id_input_meas[i]))
                        ax.plot(Ug_input_meas, sqrt_Id_data, color=colors[i], label=labels[i])
                    
                    ax.axvline(average_vth, color='k', linestyle='--', label=f"Average Vth = {average_vth:.2f}")
                    ax.set_title("IGZO TFT Vth Calculations")
                    ax.set_xlabel("Gate Voltage (V)")
                    ax.set_ylabel("Square root of Drain Current")
                    ax.legend(fontsize=8)                     

                    canvas.fig_agg = FigureCanvasTkAgg(fig, master=canvas)
                    canvas.fig_agg.draw()
                    canvas.fig_agg.get_tk_widget().pack(side="top", fill="both", expand=True)
                self.after(0, plot3, self.plot_canvases[2])

            return Vth

        Vth = func_vth(Id_input_meas, Ug_input_meas, plot=True)
        print(f"Average Vth = {Vth :.2f} V")


        ################################### mobility calc ######################################
        Udconst_values = [0.1, 5.1, 10.1, 15.1]
        def func_mobility(Ug_input_meas, Id_input_meas, Udconst_values, Vth, W, L, C_ox):
            def calc_saturation_mobility_from_input(Id, Ug, Udconst, W, L, C_ox, Vth):
                # Select the saturation region where Ug > Udconst + Vth
                sat_region = Ug > (Udconst + Vth)
                Id_sat = Id[sat_region]
                Ug_sat = Ug[sat_region]
                
                # Calculate the saturation mobility
                mobility = (2 * Id_sat) / (C_ox * W/L * (Ug_sat - Vth)**2)
                return np.mean(mobility)

            mobilities = []
            for i in range(1,len(Id_input_meas)):  # for each set of Ids corresponding to a specific Udconst
                Id = Id_input_meas[i]
                Ug = Ug_input_meas
                Udconst = Udconst_values[i]
                mobility = calc_saturation_mobility_from_input(Id, Ug, Udconst, W, L, C_ox, Vth)
                mobilities.append(mobility)
            # Calculate the average mobility
            average_mobility = np.mean(mobilities) * 1e4  # Convert from m^2/Vs to cm^2/Vs
            return average_mobility

        # Usage
        average_mobility_input = func_mobility(Ug_input_meas, Id_input_meas, Udconst_values, Vth, W, L, C_ox)
        print(f"Average saturation mobility from input characteristics = {average_mobility_input} cm^2/Vs")
        u0 = average_mobility_input


        #################### kappa ########################################
        def calculate_kappa(Id_input_meas, Ug_input_meas):
            # Calculate the logarithm of the Id values
            log_Id = np.log10(np.abs(Id_input_meas))

            # Calculate the derivative of log10(Id) with respect to Vg
            dlog_Id_dVg = np.gradient(log_Id, Ug_input_meas)

            # Find the minimum value of the derivative
            min_dlog_Id_dVg = np.min(dlog_Id_dVg)

            # Calculate kappa from the minimum derivative value
            kappa = 1 / (1 - min_dlog_Id_dVg)
            return kappa

        kappa_list = []

        for i in range(4):
            kappa_i = calculate_kappa(Id_input_meas[i], Ug_input_meas)
            kappa_list.append(kappa_i)

        mean_kappa = np.mean(kappa_list)
        print(f"Average Kappa: {mean_kappa:.3f}")


        ##################### eta ############################################
        def calculate_eta_from_output(Id_output_meas, Ud_output_meas, Ug_output, Vth, kappa):
            eta_list = []
            for i, Id_data in enumerate(Id_output_meas):
                # Choose a dataset where Vgs is close to the subthreshold region
                if Ug_output[i] < Vth:
                    continue

                # Linearize the equation by taking the natural logarithm of both sides
                ln_Id = np.log(np.abs(Id_data))

                # Perform a linear regression on the plot of ln(Id) vs Vds
                slope, _ = np.polyfit(Ud_output_meas, ln_Id, 1)

                # Slope is equal to eta
                eta = slope
                eta_list.append(eta)

            # Calculate the average eta value
            mean_eta = np.mean(eta_list)
            return mean_eta

        mean_eta = calculate_eta_from_output(Id_output_meas, Ud_output_meas, Ug_output, Vth, mean_kappa)
        print(f"Average Eta (from output characteristics): {mean_eta:.3f}")

        #################### lambda ###########################################
        def calculate_lambda(Ud_output_meas, Id_output_meas):
            # Calculate the derivative of Id with respect to Ud
            dId_dUd = np.gradient(Id_output_meas, axis=1) / np.gradient(Ud_output_meas)

            # Calculate LAMBDA as the average of the derivatives in the saturation region
            LAMBDA = np.mean(dId_dUd[:, -10:])  # Using the last 10 points in the saturation region

            return LAMBDA

        LAMBDA = calculate_lambda(Ud_output_meas, Id_output_meas)
        print(f"LAMBDA = {LAMBDA} V^-1")

        ####################### ECRIT ########################################
        def estimate_ecrit(u0):
            Vsat = 1e7  # cm/s
            ECRIT = Vsat / u0
            return ECRIT

        ECRIT = estimate_ecrit(u0)
        print(f"Estimated ECRIT = {ECRIT} V/cm")

        ####################### VMAX ########################################
        def calculate_vmax(ECRIT, Ug_input_meas, t_dielectric):
            E_peak = np.max(Ug_input_meas) / t_dielectric
            VMAX = ECRIT * E_peak
            return VMAX

        VMAX = calculate_vmax(ECRIT, Ug_input_meas, t_dielectric)
        print(f"VMAX = {VMAX} m/s")

        ####################### KP ########################################
        def calculate_kp(Ug_input_meas, Id_input_meas, Vth, W, L):
            # Calculate the derivative of Id with respect to Vg
            gm = np.gradient(Id_input_meas, axis=1) / np.gradient(Ug_input_meas)

            # Select the linear region where (Vg - Vth) is small
            linear_region_mask = (Ug_input_meas - Vth) < 1.0

            # Calculate KP using the average gm in the linear region
            KP = np.mean(gm[:, linear_region_mask]) / (W / L)
            
            return KP

        KP = calculate_kp(Ug_input_meas, Id_input_meas, Vth, W, L)
        print(f"KP (BETA) = {KP} A/V^2")

        ########################## netlist ###########################################
        def generate_netlist(vto, u0, kappa, eta, LAMBDA, nfs=2e12, nsub=1e15, theta=-0.02):
            netlist_input = f"""*
            vdd nvdd 0 10
            vprob nvdd nvdd1 0
            vprob2 nvdd nvdd2 0
            vgg nvgg 0 10
            m1 nvdd1 nvgg 0 0 testfet w={width}u l={length}u
            m2 nvdd2 nvgg 0 nvdd2 testfet w={width}u l={length}u
            
            .model testfet nmos level=3 
            +is=0 
            * Must be zero to shut off bulk diode influence (no bulk in TFT)
            +u0={u0}	
             * Mobility (approx hlaf extracted value, because we extract with t=130nm)
            +vto={vto}
            * Threshold voltage
            +gamma=0
            +pb=0   
            +fc=0 
            +tpg=0 
            * Type of gate aluminum (no influence)
            +tox={t_dielectric} 
            * Actual gate oxide thickness (for SiO2)
            +eta={eta} 
            * Theshold voltage shift with higher drain voltage. Increases slope of output current but creates unrealistic shift between input curves
            +nfs={nfs} 
            *Influences sub threshold slope
            +nsub={nsub} 
            * Substrate doping. Must be set to some value to make kappa work (physically nonsense for TFT)
            +kappa={kappa}
            * Output resistance coeficient. Higher value for lower output resistance
            +theta={theta}
            * Mobility decrease with field. Be very careful with negative values!!
            +lambda={LAMBDA}
            * Channel length modulation.
            
            .dc vgg -10 20 0.5 vdd 0.1 15.1 5
            .control
            run
            wrdata input.dat i(vprob)
            quit 
            .endc
            .end"""

            with open('input.cir', 'w') as f:
                f.write(netlist_input)    
            
            netlist_output = f"""* 
            vdd nvdd 0 10
            vprob nvdd nvdd1 0
            vprob2 nvdd nvdd2 0
            vgg nvgg 0 10
            m1 nvdd1 nvgg 0 0 testfet w={width}u l={length}u
            m2 nvdd2 nvgg 0 nvdd2 testfet w={width}u l={length}u
            .model testfet nmos level=3 
            
            +is=0 
            * Must be zero to shut off bulk diode influence (no bulk in TFT)
            +u0={u0}
             * Mobility (approx hlaf extracted value, because we extract with t=130nm)
            +vto={vto}
            * Threshold voltage
            +gamma=0
            +pb=0   
            +fc=0 
            +tpg=0 
            * Type of gate aluminum (no influence)
            +tox={t_dielectric}
            * Actual gate oxide thickness (for SiO2)
            +eta={eta}
            * Theshold voltage shift with higher drain voltage. Increases slope of output current but creates unrealistic shift between input curves
            +nfs={nfs}
            *Influences sub threshold slope
            +nsub={nsub} 
            * Substrate doping. Must be set to some value to make kappa work (physically nonsense for TFT)
            +kappa={kappa}
            * Output resistance coeficient. Higher value for lower output resistance
            +theta={theta}
            * Mobility decrease with field. Be very careful with negative values!!
            +lambda={LAMBDA}
            * Channel length modulation.
            
            .dc vdd 0 20 0.5 vgg 0 20 4
            .control
            run
            wrdata output.dat i(vprob)
            quit
            .endc
            .end"""

            with open('output.cir', 'w') as f:
                f.write(netlist_output)

                            
        # Function to run ngspice and return the simulation output
        def run_ngspice():
            with open(os.devnull, 'w') as DEVNULL:
                process1 = subprocess.Popen(['ngspice', '-b', 'input.cir'], stdout=DEVNULL, stderr=DEVNULL)
                process2 = subprocess.Popen(['ngspice', '-b', 'output.cir'], stdout=DEVNULL, stderr=DEVNULL)
            
                process1.wait()
                process2.wait()
              
            data_input = np.loadtxt('input.dat')
            data_output = np.loadtxt('output.dat')
            
            Ug_input_sim = data_input[61:122, 0]
            vprob_input = data_input[:, 1]
            Id_values_sim_input = np.vstack([vprob_input[0:61], vprob_input[61:122], vprob_input[122:183], vprob_input[183:244]])
            
            Ud_output_sim = data_output[41:82, 0]
            vprob_output = data_output[:, 1]
            Id_values_sim_output = np.vstack([vprob_output[0:41], vprob_output[41:82], vprob_output[82:123], vprob_output[123:164], vprob_output[164:205], vprob_output[205:246]])
            return np.array(Ug_input_sim), np.array(Id_values_sim_input), np.array(Ud_output_sim), np.array(Id_values_sim_output)


        def find_slope_change_index1(Id_data, Ug_array, window_size=5):
            log_Id_data = np.log10(np.abs(Id_data))
            slopes = np.diff(log_Id_data) / np.diff(Ug_array)
            moving_avg_slopes = np.convolve(slopes, np.ones(window_size), 'valid') / window_size
            slope_change_index = np.argmax(np.diff(moving_avg_slopes))
            return slope_change_index + window_size - 1
        
        def find_slope_change_index(Id_data, Ug_array, window_size=5):
            log_Id_data = np.log10(np.abs(Id_data))
            # Calculate the slopes (first derivative)
            slopes = np.diff(log_Id_data) / np.diff(Ug_array)
            # Calculate the second derivative (slope2)
            slope2 = np.diff(slopes) / np.diff(Ug_array[:-1])
            moving_avg_accelerations = np.convolve(slope2, np.ones(window_size), 'valid') / window_size
            # Find the index of the maximum slope2 (greatest change in slope)
            slope_change_index = np.argmax(np.abs(moving_avg_accelerations))
            return slope_change_index + window_size

        def normalize_data(data):
            min_val = np.min(data)
            max_val = np.max(data)
            return (data - min_val) / (max_val - min_val)
        
        def deviation(x):
             vto, u0, kappa, eta, LAMBDA, nfs, nsub, theta  = x

             generate_netlist(vto, u0, kappa, eta, LAMBDA, nfs, nsub, theta)
             Ug_input_sim, Id_values_sim_input, Ud_output_sim, Id_values_sim_output = run_ngspice()

             log_Id_input_meas = np.log10(np.abs(Id_input_meas))
             log_Id_values_sim_input = np.log10(np.abs(Id_values_sim_input))

             deviation_input_vals = []
             cnt=0
             for ids_input in log_Id_values_sim_input:
                 slope_change_index = find_slope_change_index(ids_input, Ug_input_sim) #To find deviation excluding sub-threshold region
                 sim_id_interp_input = np.interp(Ug_input_meas, Ug_input_sim, ids_input)
                 deviation_input_val = np.sum((log_Id_input_meas[cnt,slope_change_index:] - sim_id_interp_input[slope_change_index:]) ** 2)
                 #print("Spalte: ",cnt, " ", deviation_input_val)
                 deviation_input_vals.append(deviation_input_val)
                 cnt=cnt+1
             deviation_mean_input = np.mean(deviation_input_vals)
             rmse_deviation_input2 = np.sqrt(np.mean(deviation_input_vals))
             mae_deviation_input = np.mean(np.abs(deviation_input_vals))

             deviation_output_vals = []
             cnt=0
             for ids_output in Id_values_sim_output:
                 sim_id_interp_output = np.interp(Ud_output_meas, Ud_output_sim, ids_output)
                 deviation_output_val = cnt*np.sum((np.log10(np.abs(Id_output_meas[cnt,2:])) - np.log10(np.abs(sim_id_interp_output[2:]))) ** 2)
                 deviation_output_vals.append(deviation_output_val)
                 cnt=cnt+1
             deviation_mean_output = np.mean(deviation_output_vals)
             rmse_deviation_output = np.sqrt(np.mean(deviation_output_vals))
             mae_deviation_output = np.mean(np.abs(deviation_output_vals))

             return rmse_deviation_output + rmse_deviation_input2


        def differential_evolution_custom(
            objective_function, 
            bounds,
            initial_guess,
            population_size=50, 
            mutation_factor=0.5, 
            crossover_probability=0.7, 
            generations=10,
            u0_sensitivity_factor=0.5):

            # Get the lower and upper bounds
            lower_bounds, upper_bounds = np.array(bounds).T

            # The size of the solution is determined by the number of bounds
            solution_size = len(bounds)

            # Initialization
            population = lower_bounds + np.random.rand(population_size, solution_size) * (upper_bounds - lower_bounds)
            population[0] = initial_guess
            best_solution = population[0]
            best_fitness = objective_function(best_solution)
            print("Generation: 0 Best Fitness: ", best_fitness)  # Print initial status

            # Evolution
            for i in range(generations):
                for j in range(population_size):
                    # Mutation
                    indices = np.arange(population_size)
                    indices = indices[indices != j]  # Exclude current solution

                    # Select five other solutions for DE/best/2/bin strategy
                    x1, x2, x3, x4, x5 = population[np.random.choice(indices, size=5, replace=False)]

                    # Modify 'u0' specifically using the u0_sensitivity_factor
                    # Create donor solution using DE/best/2/bin strategy
                    donor = best_solution + mutation_factor * (x1 - x2 + x3 - x4) 
                    #donor[1] += np.random.normal(0, u0_sensitivity_factor)  # Assuming 'u0' is the second parameter in the solution

                    # Make sure the donor is within the bounds
                    donor = np.clip(donor, lower_bounds, upper_bounds)

                    # Crossover
                    trial = population[j].copy()  # Start with the current solution
                    for k in range(solution_size):
                        if np.random.rand() < crossover_probability:
                            trial[k] = donor[k]  # Swap this value with the donor

                    # Selection
                    trial_fitness = objective_function(trial)
                    if trial_fitness < objective_function(population[j]):  # If the trial solution is better
                        population[j] = trial  # Replace the current solution
                        if trial_fitness < best_fitness:  # If it's the best solution so far
                            best_fitness = trial_fitness
                            best_solution = trial

                # Print status for every second generation
                if (i+1) % 2 == 0:
                    print("Generation: ", i+1, " Best Fitness: ", best_fitness)

            return best_solution, best_fitness


        # Initial guesses for vto, u0, eta, kappa
        nfs=2e12
        nsub=1e15
        theta=-0.02
        mean_eta=3
        initial_guess = [Vth, u0, mean_kappa, mean_eta, LAMBDA, nfs, nsub, theta]
        bounds = [
            (Vth - 1, Vth + 1),
            (u0 - u0/2, u0 + u0/2),
            (mean_kappa, mean_kappa + 1),
            (mean_eta - 0.5, mean_eta + 0.5),
            (LAMBDA - LAMBDA/2, LAMBDA + LAMBDA/2),
            (nfs - nfs/2, nfs + nfs/2),
            (nsub - 3*nsub/4, nsub + 3*nsub/4),
            (theta - 0.005, theta + 0.005)
        ]

        selected_algorithm = self.algorithm_combo.get()
    
        if algorithm == "Differential Evolution":
            iterations = int(self.iterations_entry.get())
            results = differential_evolution(deviation, bounds, maxiter=iterations, seed=42, disp=True)
            vto_opt, u0_opt, kappa_opt, eta_opt, LAMBDA_opt, nfs_opt, nsub_opt, theta_opt = results.x
        elif algorithm == "Differential Evolution Custom":
            iterations = int(self.iterations_entry.get())
            population_size = int(self.population_size_entry.get())
            mutation_factor = float(self.mutation_factor_entry.get())
            crossover_probability = float(self.crossover_prob_entry.get())
            best_solution, best_fitness = differential_evolution_custom(deviation, bounds, initial_guess, population_size, mutation_factor, crossover_probability, iterations)
            vto_opt, u0_opt, kappa_opt, eta_opt, LAMBDA_opt, nfs_opt, nsub_opt, theta_opt = best_solution
        
    
        # Print the final optimized parameter values
        print("Final Parameter Values:")
        print(f"VTO: {vto_opt}")
        print(f"U0: {u0_opt}")
        print(f"kappa: {kappa_opt}")
        print(f"eta: {eta_opt}")
        print(f"LAMBDA: {LAMBDA_opt}")
        print(f"nfs: {nfs_opt}")
        print(f"nsub: {nsub_opt}")
        print(f"theta: {theta_opt}")


        # Plot measured and simulated data
        generate_netlist(vto_opt, u0_opt, kappa_opt, eta_opt, LAMBDA, nfs_opt, nsub_opt, theta_opt)
        #generate_netlist(Vth, u0, mean_kappa, mean_eta, nfs, nsub, theta)
        Ug_input_sim,Id_values_sim_input,Ud_output_sim,Id_values_sim_output = run_ngspice()

        log_Id_input_meas = np.log10(np.abs(Id_input_meas))
        log_Id_values_sim_input = np.log10(np.abs(Id_values_sim_input))

        # Calculate the 20% error bounds
        error_input_meas = 0.1 * Id_input_meas
        error_input_sim = 0.1 * Id_values_sim_input

        log_error_input_meas = 0.1 * log_Id_input_meas
        log_error_input_sim = 0.1 * log_Id_values_sim_input

        error_output_meas = 0.1 * Id_output_meas
        error_output_sim = 0.1 * Id_values_sim_output

        colors_meas_input = ["r", "g", "b", "m"]
        colors_sim_input = ["r", "g", "b", "m"]
        labels_input = ["Udconst = 0.1", "Udconst = 5.1", "Udconst = 10.1", "Udconst = 15.1"]
        # Plot the data        
        def plot4(canvas):
            fig, ax = plt.subplots()
            for i in range(4):
                ax.plot(Ug_input_meas, Id_input_meas[i], 'o', label="Measured"+labels_input[i], color=colors_meas_input[i])
                ax.plot(Ug_input_sim, Id_values_sim_input[i], '-', label="Simulated"+labels_input[i], color=colors_sim_input[i])
                ax.fill_between(Ug_input_meas, Id_input_meas[i] - error_input_meas[i], Id_input_meas[i] + error_input_meas[i], alpha=0.1, color=colors_meas_input[i])
                #ax.fill_between(Ug_input_sim, Id_values_sim_input[i] - error_input_sim[i], Id_values_sim_input[i] + error_input_sim[i], alpha=0.1, color=colors_sim_input[i])
            ax.set_title("Measured and Simulated Input Characteristics")
            ax.set_xlabel("Ug (V)")
            ax.set_ylabel("Id (A)")
            ax.legend(fontsize=8)  

            canvas.fig_agg = FigureCanvasTkAgg(fig, master=canvas)
            canvas.fig_agg.draw()
            canvas.fig_agg.get_tk_widget().pack(side="top", fill="both", expand=True)

        def plot5(canvas):
            fig, ax = plt.subplots()
            for i in range(4):
                ax.plot(Ug_input_meas, log_Id_input_meas[i], 'o', label="Measured"+labels_input[i], color=colors_meas_input[i])
                ax.plot(Ug_input_sim, log_Id_values_sim_input[i], '-', label="Simulated"+labels_input[i], color=colors_sim_input[i])
                ax.fill_between(Ug_input_meas, log_Id_input_meas[i] - log_error_input_meas[i], log_Id_input_meas[i] + log_error_input_meas[i], alpha=0.1, color=colors_meas_input[i])
            ax.set_title("Measured and Simulated Input log Characteristics")
            ax.set_xlabel("Ug (V)")
            ax.set_ylabel("Id (A)")
            ax.legend(fontsize=8)  
            canvas.fig_agg = FigureCanvasTkAgg(fig, master=canvas)
            canvas.fig_agg.draw()
            canvas.fig_agg.get_tk_widget().pack(side="top", fill="both", expand=True)
        

        # Plot the data
        def plot6(canvas):
            fig, ax = plt.subplots()
            colors_meas_output = ["r", "g", "b", "m", "y", "c"]
            colors_sim_output = ["r", "g", "b", "m", "y", "c"]
            labels_output = ["Ugconst = 0", "Ugconst = 4", "Ugconst = 8", "Ugconst = 12", "Ugconst = 16", "Ugconst = 20"]
            for i in range(6):
                ax.plot(Ud_output_meas, Id_output_meas[i], 'o', color=colors_meas_output[i], label="Measured"+labels_output[i])
                ax.plot(Ud_output_sim, Id_values_sim_output[i], '-', color=colors_sim_output[i], label="Simulated"+labels_output[i])
                ax.fill_between(Ud_output_meas, Id_output_meas[i] - error_output_meas[i], Id_output_meas[i] + error_output_meas[i], alpha=0.1, color=colors_meas_output[i])
            ax.set_title("Measured and Simulated Output Characteristics")
            ax.set_xlabel("Ud (V)")
            ax.set_ylabel("Id (A)")
            ax.legend(fontsize=8)  
            canvas.fig_agg = FigureCanvasTkAgg(fig, master=canvas)
            canvas.fig_agg.draw()
            canvas.fig_agg.get_tk_widget().pack(side="top", fill="both", expand=True)
        
        
        self.after(0, plot4, self.plot_canvases[3])
        self.after(0, plot5, self.plot_canvases[4])
        self.after(0, plot6, self.plot_canvases[5])


        # Update the output parameters section with the final predicted output
        output = f"Final Parameter Values:\n\n"
        output += f"Threshold Voltage - Vth (V): {vto_opt}\n"
        output += f"Mobility - U0 (cm^2/Vs): {u0_opt}\n"
        output += f"Output Resistance Coefficient - kappa: {kappa_opt}\n"
        output += f"Static Feedback Factor for Adjusting Threshold - eta: {eta_opt}\n"
        output += f"Channel Length Modulation - LAMBDA (V^-1): {LAMBDA_opt}\n"
        output += f"Bulk Charge Effect Parameter - nfs: {nfs_opt}\n"
        output += f"Bulk Surface Doping - nsub (cm^-3): {nsub_opt}\n"
        output += f"Mobility Degradation Factor - theta (V^-1): {theta_opt}\n"

        self.output_parameters_text.delete(1.0, tk.END)
        self.output_parameters_text.insert(tk.END, output)
        
if __name__ == "__main__":
    app = GUI()
    app.protocol("WM_DELETE_WINDOW", app.on_close)
    app.mainloop()
