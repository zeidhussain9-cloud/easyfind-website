# WhatsApp Lead Management UI

## Overview

This project is a simple UI for managing leads from WhatsApp numbers. The UI is built using React and integrates with a Google Sheet database to track lead information.

## Features

- Display leads from WhatsApp numbers
- View detailed information for each lead
- Direct WhatsApp access from the UI
- Change the status of leads

## Project Structure

- `src/` - Contains the React application code
- `public/` - Contains static files
- `render.yaml` - Configuration file for Render deployment

## Getting Started

1. Install dependencies with `npm install`
2. Start the development server with `npm start`
3. Deploy to Render using the configuration in `render.yaml`

## Dependencies

- React
- React Router
- Axios
- Google Sheets API client

## Deployment

- The UI is deployed on Render
- Environment variables for Google Sheets API credentials are required

## Verification

- Unit tests for all components
- Integration tests for Google Sheets API
- End-to-end tests for user flows
- Performance testing with realistic data volumes