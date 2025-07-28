import React, { ErrorInfo, ReactNode } from "react";

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
}

export class ReactErrorBoundary extends React.Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // For DOM manipulation errors, don't show error state
    if (
      error.message?.includes('removeChild') || 
      error.message?.includes('not a child') || 
      error.message?.includes('Failed to execute') ||
      error.message?.includes('The node to be removed') ||
      error.name === 'NotFoundError'
    ) {
      return { hasError: false };
    }
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // Handle specific DOM manipulation errors gracefully and silently
    if (
      error.message?.includes('removeChild') || 
      error.message?.includes('not a child') || 
      error.message?.includes('Failed to execute') ||
      error.message?.includes('The node to be removed') ||
      error.name === 'NotFoundError' ||
      errorInfo.componentStack?.includes('onfido')
    ) {
      // These are expected when third-party libraries (like Onfido) manipulate DOM
      // Reset error state immediately for DOM errors without any logging
      this.setState({ hasError: false, error: undefined });
      return;
    }
    
    // Only log non-DOM manipulation errors
    console.error('ReactErrorBoundary caught an error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      // For DOM manipulation errors, show a minimal error state
      if (this.state.error?.message?.includes('removeChild') || this.state.error?.message?.includes('not a child')) {
        return (
          <div style={{ 
            display: 'flex', 
            justifyContent: 'center', 
            alignItems: 'center', 
            minHeight: '200px',
            padding: '20px'
          }}>
            <div>Loading verification widget...</div>
          </div>
        );
      }

      return (
        <div style={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          height: '100vh',
          flexDirection: 'column',
          padding: '20px',
          textAlign: 'center'
        }}>
          <h2>Something went wrong</h2>
          <p>We're sorry, but something unexpected happened. Please refresh the page and try again.</p>
          <button 
            onClick={() => this.setState({ hasError: false, error: undefined })}
            style={{
              padding: '10px 20px',
              background: '#007bff',
              color: 'white',
              border: 'none',
              borderRadius: '5px',
              cursor: 'pointer',
              marginTop: '20px'
            }}
          >
            Try Again
          </button>
        </div>
      );
    }

    return this.props.children;
  }
}