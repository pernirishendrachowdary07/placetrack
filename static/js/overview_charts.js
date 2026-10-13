// PlaceTrack - Admin Overview Charts with Chart.js
// Loads placement metrics and chart datasets asynchronously from the JSON analytics endpoint

document.addEventListener('DOMContentLoaded', function () {
    loadAdminAnalytics();
});

async function loadAdminAnalytics() {
    const loadingIndicators = document.querySelectorAll('.chart-loading');

    try {
        const response = await fetch('/accounts/api/analytics/');
        if (!response.ok) {
            throw new Error(`Server returned HTTP ${response.status}`);
        }

        const data = await response.json();

        // 1. Update the 4 Stat Cards
        if (data.stats) {
            updateStat('stat-open-jobs', data.stats.open_jobs);
            updateStat('stat-applications', data.stats.total_applications);
            updateStat('stat-shortlisted-beyond', data.stats.shortlisted_or_beyond);
            updateStat('stat-selected', data.stats.selected);
        }

        // Hide loading spinners
        loadingIndicators.forEach(el => el.style.display = 'none');

        // 2. Render Chart 1: Applications per Company (Vertical Bar Chart)
        renderCompanyChart(data.company_chart);

        // 3. Render Chart 2: Top Missing Skills Across Applicants (Horizontal Bar Chart)
        renderSkillsChart(data.skills_chart);

    } catch (error) {
        console.error('Failed to load admin analytics:', error);
        loadingIndicators.forEach(el => {
            el.textContent = 'Failed to load chart data. Please refresh the page.';
            el.style.color = '#dc2626';
        });
    }
}

function updateStat(elementId, value) {
    const el = document.getElementById(elementId);
    if (el) {
        el.textContent = value;
    }
}

function renderCompanyChart(chartData) {
    const ctx = document.getElementById('companyApplicationsChart');
    if (!ctx || !chartData) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Applications',
                data: chartData.data,
                backgroundColor: 'rgba(37, 99, 235, 0.85)',
                borderColor: '#2563eb',
                borderWidth: 1,
                borderRadius: 6,
                maxBarThickness: 45,
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return ` ${context.parsed.y} applications submitted`;
                        }
                    }
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        precision: 0
                    },
                    grid: {
                        color: 'rgba(226, 232, 240, 0.6)'
                    }
                },
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        autoSkip: false,
                        maxRotation: 35,
                        minRotation: 20
                    }
                }
            }
        }
    });
}

function renderSkillsChart(chartData) {
    const ctx = document.getElementById('missingSkillsChart');
    if (!ctx || !chartData) return;

    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: chartData.labels,
            datasets: [{
                label: 'Missing Count',
                data: chartData.data,
                backgroundColor: 'rgba(225, 29, 72, 0.8)',
                borderColor: '#e11d48',
                borderWidth: 1,
                borderRadius: 6,
                maxBarThickness: 32,
            }]
        },
        options: {
            indexAxis: 'y', // Horizontal bars for clean readability of skill labels
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return ` Missing in ${context.parsed.x} candidate resumes`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    beginAtZero: true,
                    ticks: {
                        stepSize: 1,
                        precision: 0
                    },
                    grid: {
                        color: 'rgba(226, 232, 240, 0.6)'
                    }
                },
                y: {
                    grid: {
                        display: false
                    }
                }
            }
        }
    });
}
