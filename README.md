# Short Video Maker: AI for Creating Engaging Vertical Videos 🎥✨

![Short Video Maker](https://img.shields.io/badge/Short%20Video%20Maker-v1.0.0-blue.svg)
[![Releases](https://img.shields.io/badge/Releases-v1.0.0-brightgreen.svg)](https://github.com/leke-adewa/short-video-maker/releases)

## Overview

Short Video Maker harnesses the power of AI to generate short vertical videos tailored for platforms like TikTok, YouTube Shorts, and Instagram Reels. This repository provides tools that simplify the video creation process, allowing users to produce high-quality content efficiently.

## Features

- **AI-Driven Video Creation**: Utilize advanced algorithms to create videos that capture attention.
- **Platform Optimization**: Generate videos specifically formatted for TikTok, YouTube Shorts, and Instagram Reels.
- **Automation Tools**: Automate repetitive tasks in video production to save time and effort.
- **User-Friendly Interface**: Designed with simplicity in mind, making it accessible for everyone.

## Getting Started

To get started with Short Video Maker, you can download the latest release from the [Releases](https://github.com/leke-adewa/short-video-maker/releases) section. 

### Prerequisites

Before using Short Video Maker, ensure you have the following installed:

- Python 3.7 or higher
- pip (Python package installer)
- FFmpeg (for video processing)

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/leke-adewa/short-video-maker.git
   cd short-video-maker
   ```

2. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

3. Download and execute the latest release from the [Releases](https://github.com/leke-adewa/short-video-maker/releases) section.

### Usage

To create a video, follow these steps:

1. Prepare your assets: Gather images, audio, and any other media you want to include.
2. Run the main script:

   ```bash
   python main.py --input your_input_file --output your_output_file
   ```

3. Customize your video settings using command-line arguments. For example:

   ```bash
   python main.py --input your_input_file --output your_output_file --duration 15 --aspect-ratio 9:16
   ```

4. Your video will be generated and saved to the specified output file.

### Command-Line Arguments

| Argument         | Description                                  |
|------------------|----------------------------------------------|
| `--input`        | Path to the input file (image/audio)        |
| `--output`       | Path to save the generated video             |
| `--duration`     | Duration of the video in seconds             |
| `--aspect-ratio` | Aspect ratio of the video (default is 9:16)  |

### Example

Here's a simple example to create a video:

```bash
python main.py --input assets/my_video.mp4 --output outputs/my_short_video.mp4 --duration 30 --aspect-ratio 9:16
```

## Topics

This project covers a variety of topics related to video creation and AI:

- **AI**: The core technology behind video generation.
- **Automation**: Tools that streamline the video-making process.
- **Gemini**: Integrations that enhance video features.
- **Reels & Shorts**: Focus on short-form content for popular platforms.
- **Video Maker**: Comprehensive tools for video production.

## Contributing

We welcome contributions from the community! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them.
4. Push to your branch and submit a pull request.

Please ensure your code adheres to the project's coding standards and includes appropriate tests.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or support, please reach out via the Issues section of the repository.

## Acknowledgments

- Thanks to the contributors who help improve this project.
- Special thanks to the developers of the libraries and tools used in this project.

## Links

- **GitHub Repository**: [Short Video Maker](https://github.com/leke-adewa/short-video-maker)
- **Releases**: Download the latest version [here](https://github.com/leke-adewa/short-video-maker/releases).

## Screenshots

![Video Example](https://example.com/video_example.png)
![User Interface](https://example.com/user_interface.png)

## Frequently Asked Questions (FAQ)

### What platforms does this tool support?

Short Video Maker is optimized for TikTok, YouTube Shorts, and Instagram Reels.

### Can I use my own media files?

Yes, you can use your own images and audio files in the video creation process.

### Is there a community for support?

Yes, you can find support in the Issues section of the GitHub repository.

### How can I report a bug?

Please report any bugs or issues in the Issues section of this repository.

### Can I suggest new features?

Absolutely! We welcome suggestions. Please open an issue to discuss new features.

## Additional Resources

- **Documentation**: Comprehensive documentation is available in the `docs` folder.
- **Tutorials**: Check out the `tutorials` folder for step-by-step guides on using Short Video Maker.
- **Community**: Join our community on Discord for discussions and support.

### Final Thoughts

Short Video Maker aims to simplify the process of creating engaging short videos. By leveraging AI, we provide tools that enhance creativity and efficiency. Explore the repository, contribute, and enjoy making videos that stand out!