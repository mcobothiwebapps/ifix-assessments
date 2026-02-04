// IFIX Assessment Timer
class AssessmentTimer {
    constructor(timeLimitMinutes = 40) {
        this.timeLimitMs = timeLimitMinutes * 60 * 1000; // Convert to milliseconds
        this.startTime = Date.now();
        this.endTime = this.startTime + this.timeLimitMs;
        this.timerInterval = null;
        this.isRunning = false;
        this.warningShown = false;
        
        // Load saved time from session if exists
        this.loadSavedTime();
    }
    
    loadSavedTime() {
        const savedEndTime = sessionStorage.getItem('assessment_end_time');
        if (savedEndTime) {
            this.endTime = parseInt(savedEndTime);
            // If time already expired, clear it
            if (Date.now() > this.endTime) {
                this.clearSavedTime();
                this.endTime = Date.now() + this.timeLimitMs;
            }
        } else {
            // Save end time to session storage
            sessionStorage.setItem('assessment_end_time', this.endTime.toString());
        }
    }
    
    clearSavedTime() {
        sessionStorage.removeItem('assessment_end_time');
    }
    
    start() {
        if (this.isRunning) return;
        
        this.isRunning = true;
        this.updateDisplay();
        
        this.timerInterval = setInterval(() => {
            this.updateDisplay();
            this.checkTime();
        }, 1000);
    }
    
    updateDisplay() {
        const now = Date.now();
        const remainingMs = Math.max(0, this.endTime - now);
        
        // Convert to minutes and seconds
        const minutes = Math.floor(remainingMs / 60000);
        const seconds = Math.floor((remainingMs % 60000) / 1000);
        
        // Update timer display
        const timerElement = document.getElementById('timer-display');
        if (timerElement) {
            timerElement.textContent = `${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
            
            // Add warning colors
            if (minutes < 5) {
                timerElement.style.color = '#ef4444'; // Red
                timerElement.style.fontWeight = 'bold';
                
                // Show warning message once
                if (!this.warningShown && minutes < 1) {
                    this.showWarning('Less than 1 minute remaining!');
                    this.warningShown = true;
                }
            } else if (minutes < 10) {
                timerElement.style.color = '#f59e0b'; // Orange
            }
        }
        
        // Update progress bar if exists
        const progressElement = document.getElementById('timer-progress');
        if (progressElement) {
            const elapsedMs = this.timeLimitMs - remainingMs;
            const progressPercent = (elapsedMs / this.timeLimitMs) * 100;
            progressElement.style.width = `${Math.min(100, progressPercent)}%`;
        }
    }
    
    checkTime() {
        const now = Date.now();
        if (now >= this.endTime) {
            this.timeUp();
        }
    }
    
    timeUp() {
        clearInterval(this.timerInterval);
        
        // Show timeout message
        this.showTimeoutMessage();
        
        // Auto-submit the form after 3 seconds
        setTimeout(() => {
            const form = document.querySelector('form');
            if (form) {
                // Create a hidden input to indicate time expiration
                const timeUpInput = document.createElement('input');
                timeUpInput.type = 'hidden';
                timeUpInput.name = 'time_up';
                timeUpInput.value = 'true';
                form.appendChild(timeUpInput);
                
                // Submit form
                form.submit();
            }
        }, 3000);
    }
    
    showWarning(message) {
        this.showMessage(message, 'warning');
    }
    
    showTimeoutMessage() {
        this.showMessage('Time is up! Assessment will be submitted automatically.', 'danger');
    }
    
    showMessage(text, type = 'info') {
        // Remove any existing message
        const existingMsg = document.getElementById('timer-message');
        if (existingMsg) existingMsg.remove();
        
        // Create message element
        const messageDiv = document.createElement('div');
        messageDiv.id = 'timer-message';
        messageDiv.className = `timer-message timer-${type}`;
        messageDiv.innerHTML = `
            <div style="
                position: fixed;
                top: 20px;
                right: 20px;
                background: ${type === 'warning' ? '#fef3c7' : '#fee2e2'};
                border: 2px solid ${type === 'warning' ? '#f59e0b' : '#ef4444'};
                color: ${type === 'warning' ? '#92400e' : '#991b1b'};
                padding: 1rem;
                border-radius: 8px;
                z-index: 1000;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);
                max-width: 300px;
            ">
                <strong>${type === 'warning' ? '⚠️ Warning' : '⏰ Time Expired'}</strong>
                <p style="margin: 0.5rem 0 0 0;">${text}</p>
            </div>
        `;
        
        document.body.appendChild(messageDiv);
        
        // Auto-remove after 5 seconds (except timeout message)
        if (type !== 'danger') {
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 5000);
        }
    }
    
    stop() {
        clearInterval(this.timerInterval);
        this.isRunning = false;
        this.clearSavedTime();
    }
}

// Initialize timer when page loads
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize on question pages
    if (window.location.pathname.includes('/question/')) {
        const timer = new AssessmentTimer(40); // 40-minute assessment
        timer.start();
        
        // Save timer instance globally for debugging
        window.assessmentTimer = timer;
        
        // Add progress bar if not exists
        if (!document.getElementById('timer-progress')) {
            const progressBar = document.createElement('div');
            progressBar.id = 'timer-progress';
            progressBar.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                height: 4px;
                background: linear-gradient(90deg, #10b981, #2563eb, #ef4444);
                width: 0%;
                transition: width 1s linear;
                z-index: 1001;
            `;
            document.body.appendChild(progressBar);
        }
        
        // Add timer display to header if not exists
        if (!document.getElementById('timer-display')) {
            const header = document.querySelector('.header-content');
            if (header) {
                const timerDisplay = document.createElement('div');
                timerDisplay.id = 'timer-display';
                timerDisplay.style.cssText = `
                    background: #1e293b;
                    color: white;
                    padding: 0.5rem 1rem;
                    border-radius: 999px;
                    font-family: monospace;
                    font-size: 1.1rem;
                    font-weight: bold;
                `;
                header.appendChild(timerDisplay);
            }
        }
        
        // Handle page unload/refresh warning - SINGLE EVENT LISTENER
        window.addEventListener('beforeunload', function(e) {
            if (timer.isRunning) {
                // Check if we're submitting a form (normal navigation)
                const isFormSubmission = e.target?.tagName === 'FORM' || 
                                        e.target?.tagName === 'BUTTON' ||
                                        e.target?.type === 'submit';
                
                // Check if we're clicking a link in our app (not external)
                const isInternalNavigation = e.target?.tagName === 'A' && 
                                           e.target?.href?.includes(window.location.origin);
                
                // Only show warning for external navigation or page close
                if (!isFormSubmission && !isInternalNavigation) {
                    e.preventDefault();
                    e.returnValue = 'Your assessment timer is still running. Are you sure you want to leave?';
                    return e.returnValue;
                }
            }
        });
        
        // Add form submission handler to prevent warnings
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', function() {
                // When form submits normally, stop the timer warning
                timer.isRunning = false;
            });
        }
    }
});