# Overview

This is a **Celebration Mosaic** web application built with Flask that allows users to submit festive messages and view them in a beautiful mosaic display. The app serves as a community celebration board where users can share messages with custom symbols (emojis) and view all submissions in an organized grid layout with a customizable background logo.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Frontend Architecture
- **Template Engine**: Jinja2 templates with Bootstrap 5 for responsive UI
- **Styling**: Custom CSS with dark theme support and mosaic grid layout
- **JavaScript**: Vanilla JS for tooltips, auto-refresh functionality, and form interactions
- **Responsive Design**: Mobile-first approach using Bootstrap's grid system

## Backend Architecture
- **Framework**: Flask web framework with Python
- **File-based Data Storage**: JSON files for persistent data storage
  - `data.json`: User submissions storage
  - `admin_settings.json`: Configuration settings
- **Session Management**: Flask sessions with configurable secret key
- **File Upload System**: Secure file handling for logo uploads with validation
- **Logging**: Built-in Python logging for debugging and monitoring

## Data Models
- **User Submissions**: Name, message, symbol (emoji), timestamp
- **Admin Settings**: Logo filename, maximum entries display limit, available symbols configuration
- **File Validation**: Restricted file types for uploads (PNG, JPG, JPEG, GIF, SVG)

## Core Features
- **Message Submission**: Form-based user input with validation
- **Mosaic Display**: Grid-based visualization of all celebrations
- **Admin Panel**: Logo management and display settings configuration
- **Real-time Updates**: Auto-refresh functionality for live mosaic updates
- **Responsive UI**: Works across desktop and mobile devices

## Security Considerations
- Input validation and sanitization for user submissions
- Secure filename handling for uploads
- File type restrictions for logo uploads
- Session secret key configuration for production deployment

# External Dependencies

## Frontend Libraries
- **Bootstrap 5.3.0**: UI framework and components via CDN
- **Bootstrap Agent Dark Theme**: Custom dark theme styling via Replit CDN

## Python Packages
- **Flask**: Web framework for routing, templating, and request handling
- **Werkzeug**: Utilities for secure filename handling and file operations

## File System Dependencies
- **Static Assets**: Logo images and CSS files stored in `/static` directory
- **JSON Storage**: Local file system for data persistence
- **Upload Directory**: Configured upload folder for logo management

## Configuration
- **Environment Variables**: `SESSION_SECRET` for production security
- **File Paths**: Configurable upload folder and allowed file extensions
- **Admin Settings**: JSON-based configuration for customizable app behavior