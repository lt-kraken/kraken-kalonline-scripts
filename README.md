# KalOnline Automation Tools

This repository contains two sets of automation tools for KalOnline: one for item fusion (`AutoFuser`) and one for item enhancement (`AutoPimper`). Each tool is designed to automate specific tasks within the game, leveraging advanced scripting and automation techniques.

## Background

The development of these tools was driven by a curiosity to explore the capabilities of OpenAI's ChatGPT in assisting with complex scripting tasks as I was (and remain to be) not very knowledgable about Python. Throughout the development process, ChatGPT provided textual guidance, which was instrumental in shaping the logic and structure of the scripts. This project serves as a testament to the potential of AI-assisted coding, showcasing how far one can go with intelligent guidance and minimal manual tweaks.

## Project Structure

- `/AutoFuser`: Contains the automation script for item fusion in KalOnline along with its specific `requirements.txt` and `README.md`.
- `/AutoPimper`: Contains the automation script for item enhancement in KalOnline along with its specific `requirements.txt` and `README.md`.
- `LICENSE`: Details the GNU General Public License under which this software is distributed.
- `README.md`: Provides an overview of the project and its background.

## Motivation

The primary motivation behind this project was to test the limits of conversational AI in software development. It was particularly focused on:
- **Exploring AI Capabilities**: Understanding the extent to which AI can assist in real-world programming tasks.
- **Automation in Gaming**: Creating tools that automate repetitive tasks in gaming, thereby enhancing the gaming experience.
- **Learning and Experimentation**: Using the project as a learning tool for advanced Python scripting and GUI automation.

## Reflections

The development journey was surprisingly smooth, considering the complexity of the tasks automated. ChatGPT's role was pivotal, offering not only code snippets but also debugging help and conceptual explanations. However, it was observed that occasional tweaks were necessary, especially in handling missing imports and optimizing some logic sequences. One thing that ChatGPT struggled with was providing a solution to click simulation, which was easily resolved after a 5-minute investigation and finding `pywinauto`. Checking my conversation with ChatGPT, I've come to the conclusion that although it did suggest using `pywinauto` at an earlier time, it was suggested the wrong methods to perform the click operations. In all situations it seemed to suggest the `click_input` operations (simulate physical click) rather than the `click` operations (simulate a virtual click). 

## Contributions

Contributions to this project are welcome. They can be made by cloning the repository, making changes, and submitting a pull request. For major changes, please open an issue first to discuss what you would like to change.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgements

- **OpenAI**: For providing the ChatGPT model which was crucial in the development of these scripts.
- **The KalOnline Community**: For providing a platform to test and refine the automation tools.

## Copyright

Copyright (C) 2024 [KrakenSoftware.eu](https://krakensoftware.eu)

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
