# AI Collab 🤖💬

A modern, multi-user AI chat application built with Flask, SQLAlchemy, and OpenAI API. Designed specifically for educational writing support, AI Collab helps students improve their writing through intelligent AI feedback across different writing stages.

## ✨ Features

### Core Functionality
- **Multi-User Support**: Register, login, and manage user profiles
- **AI Chat Integration**: Powered by OpenAI GPT-4o for intelligent responses
- **Chat Management**: Create, edit, delete, and organize your conversations
- **Sharing & Collaboration**: Share chats with other users with customizable permissions
- **Public/Private Chats**: Make chats public for community discovery or keep them private

### Educational Writing Support
- **Writing Mode System**: 10 different writing stages (Explore, Focus, Outline, Draft, Revise, Polish, etc.)
- **Mode-Specific AI Prompts**: AI adapts its responses based on the current writing stage
- **Google Docs Integration**: Import and analyze Google Docs directly into chats
- **Document Analysis**: Get AI feedback on your writing without importing text

### Analytics & Dashboard
- **Student Analytics**: Track student prompts and writing modes
- **Prompt Recording**: Monitor how students use AI assistance
- **Mode Filtering**: Analyze usage patterns by writing stage
- **User Insights**: Understand student writing workflows

### Modern UI
- **Clean Design**: Responsive, intuitive user experience
- **Real-time Messaging**: Seamless conversation flow with AI assistant
- **Access Control**: Secure permission system with decorators

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key
- Google Cloud Project (for Google Docs integration)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/writeian/Collab.AI.git
   cd Collab.AI
   ```

2. **Create and activate virtual environment**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Create a `.env` file in the project root:
   ```env
   OPENAI_API_KEY=your_openai_api_key_here
   SECRET_KEY=your_secret_key_here
   GOOGLE_SERVICE_ACCOUNT_FILE=service-account-key.json
   ```

5. **Set up Google Docs Integration (Optional)**
   - Follow the setup guide in `GOOGLE_DOCS_SETUP.md`
   - Place your service account key file as `service-account-key.json`

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open your browser**
   Navigate to `http://127.0.0.1:5000`

## 📁 Project Structure

```
AI_Collab/
├── app.py                 # Main Flask application
├── models.py              # SQLAlchemy database models
├── openai_utils.py        # OpenAI API integration & writing modes
├── google_docs.py         # Google Docs integration utilities
├── chat.py                # Chat routes and functionality
├── auth.py                # Authentication routes
├── dashboard.py           # Analytics dashboard
├── access_control.py      # Permission decorators
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── GOOGLE_DOCS_SETUP.md  # Google Docs setup guide
├── Static/
│   └── style.css         # CSS styling
└── Templates/
    ├── base.html         # Base template
    ├── index.html        # Home page
    ├── login.html        # Login page
    ├── register.html     # Registration page
    ├── profile.html      # User profile
    ├── create_chat.html  # Create new chat (with Google Docs URL)
    ├── view_chat.html    # View chat conversation
    ├── edit_chat.html    # Edit chat settings
    ├── delete_chat.html  # Delete confirmation
    ├── admin_users.html  # Admin user listing
    └── dashboard/
        ├── index.html    # Dashboard overview
        └── prompts.html  # Prompt analytics
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

- `OPENAI_API_KEY`: Your OpenAI API key (required)
- `SECRET_KEY`: Flask secret key for sessions (optional, defaults to "dev")
- `GOOGLE_SERVICE_ACCOUNT_FILE`: Path to Google service account key (optional)

### Database

The application uses SQLite by default. The database file (`ai_collab.db`) will be created automatically in the project root on first run.

### Google Docs Integration

For Google Docs functionality:
1. Create a Google Cloud Project
2. Enable Google Docs API
3. Create a service account
4. Download the JSON key file
5. Share documents with the service account email

See `GOOGLE_DOCS_SETUP.md` for detailed instructions.

## 🎯 Usage

### Getting Started

1. **Register an account** at `/register`
2. **Create your first chat** at `/create`
3. **Select a writing mode** (Explore, Focus, Outline, etc.)
4. **Optionally add a Google Doc URL** to import content
5. **Start chatting** with the AI assistant
6. **Share chats** with other users for collaboration

### Writing Modes

AI Collab supports 10 different writing stages:

1. **Explore** - Brainstorming and idea generation
2. **Focus** - Narrowing down topics and research questions
3. **Outline** - Creating structure and organization
4. **Draft** - Initial writing and content creation
5. **Revise** - Improving content and structure
6. **Polish** - Final editing and refinement
7. **Proposal** - Writing proposals and pitches
8. **Research** - Finding and evaluating sources
9. **Context** - Understanding background information
10. **Feedback** - Getting and incorporating feedback

### Google Docs Integration

1. **Share your Google Doc** with the service account email
2. **Copy the sharing link** from Google Docs
3. **Paste the URL** in the "Google Doc URL" field when creating a chat
4. **The AI will analyze** your document and provide feedback
5. **Continue the conversation** to get more specific guidance

### Dashboard Analytics

- **View prompt analytics** at `/dashboard`
- **Filter by writing mode** to see usage patterns
- **Track student progress** through different writing stages
- **Monitor AI assistance** usage across your class

## 🛠️ Technology Stack

- **Backend**: Flask, SQLAlchemy
- **Database**: SQLite
- **AI Integration**: OpenAI API (GPT-4o)
- **Google Integration**: Google Docs API with service account
- **Frontend**: HTML, CSS, JavaScript
- **Authentication**: Flask-SQLAlchemy with password hashing
- **Access Control**: Custom decorators for permissions
- **Analytics**: Dashboard for tracking student usage

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenAI for providing the GPT-4o API
- Google Cloud for Google Docs API
- Flask community for the excellent web framework
- SQLAlchemy for robust database management

## 📞 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/writeian/Collab.AI/issues) page
2. Create a new issue with detailed information
3. Include your Python version, OS, and error messages

## 🔮 Roadmap

- [x] Google Docs integration with service account
- [x] Writing mode system with 10 stages
- [x] Dashboard analytics for student tracking
- [x] Access control with permission decorators
- [ ] Real-time messaging with WebSockets
- [ ] Advanced chat analytics
- [ ] Mobile-responsive design improvements
- [ ] Multi-language support
- [ ] Chat export functionality
- [ ] Integration with learning management systems

---

**Made with ❤️ by writeian**
