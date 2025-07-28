const Preloader = () => {
    return (
        <div className="preloader">
            <svg
                viewBox="0 0 100 100"
                xmlns="http://www.w3.org/2000/svg"
                className="w-48 h-48"
                height={80}
                width={80}
            >
                <g
                    style={{
                        animation: "spin-fast 1.2s linear infinite",
                        transformOrigin: "50% 50%"
                    }}
                >
                    <path
                        d="M90.75,30.91c-0.88-1.87-3.15-2.61-4.94-1.58l-0.01,0.01c1.79-1.03,2.29-3.37,1.11-5.06C79.47,13.61,67.53,6.32,53.84,5.16 
                        C51.78,4.99,50,6.58,50,8.65v0.01c0-2.06-1.77-3.67-3.83-3.49c-12.96,1.12-25.24,7.81-33.09,19.08c-1.18,1.7-0.69,4.04,1.1,5.07 
                        l2.8,1.62l-2.79-1.61c-1.79-1.03-4.06-0.3-4.94,1.57C3.75,42.68,3.41,56.66,9.25,69.09c0.88,1.87,3.15,2.61,4.94,1.58l7.66-4.42 
                        c-6.01-10.42-5.6-22.77,0-32.5l0,0C27.87,23.33,38.78,17.51,50,17.5v0c12.03,0,22.52,6.54,28.14,16.25l0,0 
                        c6.01,10.42,5.6,22.77,0,32.5l0,0C72.13,76.67,61.22,82.49,50,82.5v8.84c0,2.06,1.77,3.67,3.83,3.49 
                        c12.96-1.12,25.24-7.81,33.09-19.08c1.18-1.7,0.69-4.04-1.1-5.07l-2.8-1.62l2.79,1.61c1.79,1.03,4.06,0.3,4.94-1.57 
                        C96.25,57.32,96.59,43.34,90.75,30.91z"
                        stroke="#323334"
                        fill="#F6B26A"
                        strokeWidth="3.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                    <path
                        d="M19.4,67.67c1.99,1.38,4.57,1.87,7.07,1.09c2.75-0.85,5.53,1.2,5.53,4.07c0,1.49,1,2.87,2.46,3.12
                        C36.36,76.28,38,74.83,38,73v-12.03c0-2.5,1.34-4.81,3.5-6.07L50,50v32.5c11.22-0.01,22.13-5.83,28.15-16.25
                        c5.6-9.72,6.02-22.08,0-32.5C72.52,24.04,62.03,17.5,50,17.5c-11.22,0.01-22.13,5.83-28.15,16.25
                        c-5.6,9.72-6.02,22.08,0,32.5L31,61"
                        stroke="#323334"
                        fill="#F5E169"
                        strokeWidth="3.5"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                    />
                    <circle cx="40" cy="32.68" r="5.5" fill="#C33836" stroke="#323334" strokeWidth="3.5" />
                    <circle cx="30" cy="50" r="5.5" fill="#C33836" stroke="#323334" strokeWidth="3.5" />
                    <circle cx="60" cy="67.32" r="5.5" fill="#C33836" stroke="#323334" strokeWidth="3.5" />
                    <circle cx="70" cy="50" r="5.5" fill="#C33836" stroke="#323334" strokeWidth="3.5" />
                    <circle cx="60" cy="32.68" r="5.5" fill="#C33836" stroke="#323334" strokeWidth="3.5" />
                </g>
            </svg>

            <p className="mt-6 text-xl font-semibold tracking-wide animate-pulse">
                Preparing something delicious...
            </p>

            <style>
                {`
                    @keyframes spin-fast {
                        0% { transform: rotate(0deg); }
                        100% { transform: rotate(360deg); }
                    }
                `}
            </style>
        </div>
    );
};

export default Preloader;
