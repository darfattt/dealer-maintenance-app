# Project Overview

This is a Vue.js web application built with Vite, utilizing PrimeVue for UI components, Pinia for state management, and Vue Router for navigation. It's based on the Sakai application template.

## Technologies Used

*   **Framework:** Vue.js 3
*   **Build Tool:** Vite
*   **UI Library:** PrimeVue
*   **State Management:** Pinia
*   **Routing:** Vue Router
*   **Styling:** Tailwind CSS, SCSS
*   **HTTP Client:** Axios

## Getting Started

Follow these steps to set up and run the project locally.

### Installation

1.  **Clone the repository:** (Assuming this is part of a larger repo, otherwise provide instructions)

2.  **Navigate to the project directory:**
    ```bash
    cd E:\darfat\work\dgi\dealer-management-app\dealer-maintenance-app\web
    ```

3.  **Install dependencies:**
    ```bash
    npm install
    ```

### Running Locally

To start the development server:

```bash
npm run dev
```

This will typically run the application on `http://localhost:5173` (or another available port).

### Building for Production

To build the application for production:

```bash
npm run build
```

The build artifacts will be generated in the `dist` directory.

### Previewing Production Build

To preview the production build locally:

```bash
npm run preview
```

### Linting

To lint and fix code style issues:

```bash
npm run lint
```

## Project Structure

Key directories and files:

*   `public/`: Static assets.
*   `src/`: Main application source code.
    *   `assets/`: Global styles, images, etc.
    *   `components/`: Reusable Vue components.
    *   `layout/`: Application layout components.
    *   `router/`: Vue Router configuration.
    *   `service/`: Data fetching and API service layers.
    *   `stores/`: Pinia stores for state management.
    *   `views/`: Page-level components.
*   `App.vue`: Main application component.
*   `main.js`: Application entry point.
*   `vite.config.mjs`: Vite configuration.
*   `tailwind.config.js`: Tailwind CSS configuration.
*   `package.json`: Project dependencies and scripts.
