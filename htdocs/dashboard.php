<?php
// Initialize the session
session_start();

// Check if the user is logged in, if not then redirect to login page
if(!isset($_SESSION["loggedin"]) || $_SESSION["loggedin"] !== true){
    header("location: login.php");
    exit;
}

// Include config file
require_once "config.php";

// Function to get dashboard statistics
function getDashboardStats($conn) {
    $stats = array();
    
    // Total users registered
    $sql = "SELECT COUNT(*) as total_users FROM users";
    $result = $conn->query($sql);
    $stats['total_users'] = $result->fetch_assoc()['total_users'];
    
    // Number of chatbot queries (placeholder - you would need a queries table)
    $stats['total_queries'] = rand(150, 300); // Static for demo, replace with actual query
    
    // Most common disease keyword (placeholder - you would need a queries table)
    $stats['common_disease'] = 'Dengue'; // Static for demo, replace with actual query
    
    // Reminders set (placeholder - you would need a reminders table)
    $stats['reminders_set'] = rand(50, 100); // Static for demo, replace with actual query
    
    return $stats;
}

// Function to get disease distribution data
function getDiseaseDistribution($conn) {
    // This would normally come from your queries/log table
    // Static data for demo
    return [
        ['Disease' => 'Dengue', 'Count' => 45],
        ['Disease' => 'Malaria', 'Count' => 32],
        ['Disease' => 'COVID-19', 'Count' => 28],
        ['Disease' => 'Typhoid', 'Count' => 18],
        ['Disease' => 'Chikungunya', 'Count' => 12]
    ];
}

// Function to get daily queries data
function getDailyQueriesData($conn) {
    // This would normally come from your queries/log table
    // Static data for demo (last 7 days)
    return [
        ['Date' => '2025-09-20', 'Queries' => 25],
        ['Date' => '2025-09-21', 'Queries' => 32],
        ['Date' => '2025-09-22', 'Queries' => 28],
        ['Date' => '2025-09-23', 'Queries' => 45],
        ['Date' => '2025-09-24', 'Queries' => 38],
        ['Date' => '2025-09-25', 'Queries' => 42],
        ['Date' => '2025-09-26', 'Queries' => 35]
    ];
}

// Function to get age distribution data
function getAgeDistribution($conn) {
    // This would normally come from your users table
    // Static data for demo
    return [
        ['AgeGroup' => '0-18', 'Count' => 15],
        ['AgeGroup' => '19-30', 'Count' => 45],
        ['AgeGroup' => '31-45', 'Count' => 38],
        ['AgeGroup' => '46-60', 'Count' => 28],
        ['AgeGroup' => '60+', 'Count' => 12]
    ];
}

// Get dashboard statistics
$stats = getDashboardStats($conn);
$diseaseData = getDiseaseDistribution($conn);
$dailyQueriesData = getDailyQueriesData($conn);
$ageDistributionData = getAgeDistribution($conn);

?>

<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard - Personal Chatbot</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            background-color: #f8f9fa;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }
        
        .navbar-brand {
            font-weight: 600;
            color: #2c3e50 !important;
        }
        
        .stats-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            transition: transform 0.3s ease;
        }
        
        .stats-card:hover {
            transform: translateY(-5px);
        }
        
        .stats-card .card-body {
            padding: 1.5rem;
        }
        
        .stats-card .display-4 {
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .stats-card .text-muted {
            color: rgba(255,255,255,0.8) !important;
        }
        
        .chart-container {
            background: white;
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }
        
        .welcome-section {
            background: linear-gradient(135deg, #74b9ff 0%, #0984e3 100%);
            color: white;
            border-radius: 15px;
            padding: 2rem;
            margin-bottom: 2rem;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .welcome-section h1 {
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        
        .navbar {
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            background: white !important;
        }
        
        .nav-link {
            font-weight: 500;
            margin: 0 5px;
            transition: color 0.3s ease;
        }
        
        .nav-link:hover {
            color: #667eea !important;
        }
        
        .nav-link.active {
            color: #667eea !important;
            font-weight: 600;
        }
        
        .btn-logout {
            background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 8px 20px;
            transition: transform 0.3s ease;
        }
        
        .btn-logout:hover {
            transform: scale(1.05);
            color: white;
        }
        
        .chart-title {
            font-weight: 600;
            color: #2c3e50;
            margin-bottom: 1rem;
            text-align: center;
        }
        
        .icon-large {
            font-size: 2.5rem;
            opacity: 0.8;
            margin-bottom: 1rem;
        }
    </style>
</head>
<body>
    <!-- Navigation Bar -->
    <nav class="navbar navbar-expand-lg navbar-light bg-white sticky-top">
        <div class="container">
            <a class="navbar-brand" href="#">
                <i class="fas fa-robot me-2"></i>Personal Chatbot
            </a>
            <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav">
                <span class="navbar-toggler-icon"></span>
            </button>
            <div class="collapse navbar-collapse" id="navbarNav">
                <ul class="navbar-nav me-auto">
                    <li class="nav-item">
                        <a class="nav-link active" href="dashboard.php">
                            <i class="fas fa-tachometer-alt me-1"></i>Dashboard
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="profile.php">
                            <i class="fas fa-user me-1"></i>Profile
                        </a>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link" href="#analytics">
                            <i class="fas fa-chart-bar me-1"></i>Analytics
                        </a>
                    </li>
                     <li class="nav-item">
                        <a class="nav-link" href="chatbot-demo.html">
                            <i class="fas fa-chart-bar me-1"></i>chatbot
                        </a>
                    </li>
                </ul>
                <ul class="navbar-nav">
                    <li class="nav-item">
                        <span class="nav-link">
                            <i class="fas fa-user-circle me-1"></i><?php echo htmlspecialchars($_SESSION["name"]); ?>
                        </span>
                    </li>
                    <li class="nav-item">
                        <a class="nav-link btn-logout" href="logout.php">
                            <i class="fas fa-sign-out-alt me-1"></i>Logout
                        </a>
                    </li>
                </ul>
            </div>
        </div>
    </nav>

    <div class="container mt-4">
        <!-- Welcome Section -->
        <div class="welcome-section">
            <div class="row align-items-center">
                <div class="col-md-8">
                    <h1>Welcome back, <?php echo htmlspecialchars($_SESSION["name"]); ?>!</h1>
                    <p class="lead mb-0">Here's what's happening with your personal health assistant today.</p>
                </div>
                <div class="col-md-4 text-center">
                    <i class="fas fa-heartbeat icon-large"></i>
                </div>
            </div>
        </div>

        <!-- Statistics Cards -->
        <div class="row mb-4">
            <div class="col-md-3 mb-3">
                <div class="card stats-card">
                    <div class="card-body text-center">
                        <i class="fas fa-users icon-large"></i>
                        <h2 class="display-4"><?php echo $stats['total_users']; ?></h2>
                        <p class="text-muted mb-0">Total Users</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card stats-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
                    <div class="card-body text-center">
                        <i class="fas fa-comments icon-large"></i>
                        <h2 class="display-4"><?php echo $stats['total_queries']; ?></h2>
                        <p class="text-muted mb-0">Chatbot Queries</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card stats-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);">
                    <div class="card-body text-center">
                        <i class="fas fa-virus icon-large"></i>
                        <h2 class="display-4"><?php echo $stats['common_disease']; ?></h2>
                        <p class="text-muted mb-0">Most Common Disease</p>
                    </div>
                </div>
            </div>
            <div class="col-md-3 mb-3">
                <div class="card stats-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);">
                    <div class="card-body text-center">
                        <i class="fas fa-bell icon-large"></i>
                        <h2 class="display-4"><?php echo $stats['reminders_set']; ?></h2>
                        <p class="text-muted mb-0">Reminders Set</p>
                    </div>
                </div>
            </div>
        </div>

        <!-- Analytics Section -->
        <div id="analytics" class="mb-5">
            <h2 class="text-center mb-4">
                <i class="fas fa-chart-line me-2"></i>Analytics Dashboard
            </h2>
            
            <div class="row">
                <!-- Disease Distribution Pie Chart -->
                <div class="col-md-4 mb-4">
                    <div class="chart-container">
                        <h4 class="chart-title">
                            <i class="fas fa-chart-pie me-2"></i>Disease Distribution
                        </h4>
                        <canvas id="diseaseChart"></canvas>
                    </div>
                </div>

                <!-- Daily Queries Line Chart -->
                <div class="col-md-8 mb-4">
                    <div class="chart-container">
                        <h4 class="chart-title">
                            <i class="fas fa-chart-line me-2"></i>Daily Chatbot Queries
                        </h4>
                        <canvas id="queriesChart"></canvas>
                    </div>
                </div>
            </div>

            <div class="row">
                <!-- Age Distribution Bar Chart -->
                <div class="col-md-12 mb-4">
                    <div class="chart-container">
                        <h4 class="chart-title">
                            <i class="fas fa-chart-bar me-2"></i>Age Distribution of Users
                        </h4>
                        <canvas id="ageChart"></canvas>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bootstrap JS -->
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>

    <!-- Chart.js Configuration -->
    <script>
        // Disease Distribution Pie Chart
        const diseaseCtx = document.getElementById('diseaseChart').getContext('2d');
        const diseaseChart = new Chart(diseaseCtx, {
            type: 'pie',
            data: {
                labels: <?php echo json_encode(array_column($diseaseData, 'Disease')); ?>,
                datasets: [{
                    data: <?php echo json_encode(array_column($diseaseData, 'Count')); ?>,
                    backgroundColor: [
                        '#FF6384',
                        '#36A2EB',
                        '#FFCE56',
                        '#4BC0C0',
                        '#9966FF'
                    ],
                    borderWidth: 2,
                    borderColor: '#fff'
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                    },
                    title: {
                        display: true,
                        text: 'Disease Categories Distribution'
                    }
                }
            }
        });

        // Daily Queries Line Chart
        const queriesCtx = document.getElementById('queriesChart').getContext('2d');
        const queriesChart = new Chart(queriesCtx, {
            type: 'line',
            data: {
                labels: <?php echo json_encode(array_column($dailyQueriesData, 'Date')); ?>,
                datasets: [{
                    label: 'Number of Queries',
                    data: <?php echo json_encode(array_column($dailyQueriesData, 'Queries')); ?>,
                    borderColor: '#667eea',
                    backgroundColor: 'rgba(102, 126, 234, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Queries'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Date'
                        }
                    }
                }
            }
        });

        // Age Distribution Bar Chart
        const ageCtx = document.getElementById('ageChart').getContext('2d');
        const ageChart = new Chart(ageCtx, {
            type: 'bar',
            data: {
                labels: <?php echo json_encode(array_column($ageDistributionData, 'AgeGroup')); ?>,
                datasets: [{
                    label: 'Number of Users',
                    data: <?php echo json_encode(array_column($ageDistributionData, 'Count')); ?>,
                    backgroundColor: [
                        'rgba(255, 99, 132, 0.8)',
                        'rgba(54, 162, 235, 0.8)',
                        'rgba(255, 206, 86, 0.8)',
                        'rgba(75, 192, 192, 0.8)',
                        'rgba(153, 102, 255, 0.8)'
                    ],
                    borderColor: [
                        'rgba(255, 99, 132, 1)',
                        'rgba(54, 162, 235, 1)',
                        'rgba(255, 206, 86, 1)',
                        'rgba(75, 192, 192, 1)',
                        'rgba(153, 102, 255, 1)'
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    },
                    title: {
                        display: true,
                        text: 'User Age Distribution'
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Number of Users'
                        }
                    },
                    x: {
                        title: {
                            display: true,
                            text: 'Age Groups'
                        }
                    }
                }
            }
        });

        // Smooth scrolling for navigation links
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                document.querySelector(this.getAttribute('href')).scrollIntoView({
                    behavior: 'smooth'
                });
            });
        });
    </script>
</body>
</html>