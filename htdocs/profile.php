<?php
// Include database configuration
require_once 'config.php';

// Start session if not already started
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}

// Check if user is logged in, if not then redirect to login page
if (!isset($_SESSION["loggedin"]) || $_SESSION["loggedin"] !== true) {
    header("Location: login.php");
    exit();
}

// Initialize variables with existing data
$name = $email = $age = $gender = $phone = $address = $medical_history = $allergies = "";
$name_err = $age_err = $phone_err = "";
$success_message = "";

// Fetch existing user data from database
$user_id = $_SESSION["id"];
$sql = "SELECT name, email, age, gender, phone, address, medical_history, allergies FROM users WHERE id = ?";

if ($stmt = $conn->prepare($sql)) {
    $stmt->bind_param("i", $user_id);
    if ($stmt->execute()) {
        $stmt->store_result();
        if ($stmt->num_rows == 1) {
            $stmt->bind_result($name, $email, $age, $gender, $phone, $address, $medical_history, $allergies);
            $stmt->fetch();
        }
    }
    $stmt->close();
}

// Process form submission when POST request is made
if ($_SERVER["REQUEST_METHOD"] == "POST") {
    
    // Validate name
    if (empty(trim($_POST["name"]))) {
        $name_err = "Please enter your name.";
    } else {
        $name = trim($_POST["name"]);
    }
    
    // Validate age (must be a positive integer)
    if (!empty($_POST["age"])) {
        $age = trim($_POST["age"]);
        if (!is_numeric($age) || $age < 0 || $age > 150) {
            $age_err = "Please enter a valid age between 0 and 150.";
        }
    }
    
    // Validate phone number (basic validation)
    if (!empty($_POST["phone"])) {
        $phone = trim($_POST["phone"]);
        // Remove any non-digit characters for validation
        $phone_digits = preg_replace('/[^0-9]/', '', $phone);
        if (strlen($phone_digits) < 10 || strlen($phone_digits) > 15) {
            $phone_err = "Please enter a valid phone number (10-15 digits).";
        }
    }
    
    // Get other form data (no validation required for these fields)
    $gender = isset($_POST["gender"]) ? trim($_POST["gender"]) : "";
    $address = isset($_POST["address"]) ? trim($_POST["address"]) : "";
    $medical_history = isset($_POST["medical_history"]) ? trim($_POST["medical_history"]) : "";
    $allergies = isset($_POST["allergies"]) ? trim($_POST["allergies"]) : "";
    
    // Check input errors before updating database
    if (empty($name_err) && empty($age_err) && empty($phone_err)) {
        
        // Prepare update statement
        $sql = "UPDATE users SET name = ?, age = ?, gender = ?, phone = ?, address = ?, medical_history = ?, allergies = ? WHERE id = ?";
        
        if ($stmt = $conn->prepare($sql)) {
            // Bind variables to the prepared statement as parameters
            $stmt->bind_param("sississi", $param_name, $param_age, $param_gender, $param_phone, $param_address, $param_medical_history, $param_allergies, $param_id);
            
            // Set parameters
            $param_name = $name;
            $param_age = !empty($age) ? $age : null;
            $param_gender = !empty($gender) ? $gender : null;
            $param_phone = !empty($phone) ? $phone : null;
            $param_address = !empty($address) ? $address : null;
            $param_medical_history = !empty($medical_history) ? $medical_history : null;
            $param_allergies = !empty($allergies) ? $allergies : null;
            $param_id = $user_id;
            
            // Attempt to execute the prepared statement
            if ($stmt->execute()) {
                // Update session name if it was changed
                $_SESSION["name"] = $name;
                $success_message = "Profile updated successfully!";
            } else {
                echo "<div class='alert alert-danger'>Oops! Something went wrong. Please try again later.</div>";
            }
            
            // Close statement
            $stmt->close();
        }
    }
    
    // Close connection
    $conn->close();
}
?>

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Patient Profile - Personal Chatbot</title>
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
  <style>
    .wrapper {
      max-width: 800px;
      padding: 20px;
      margin: 0 auto;
      margin-top: 30px;
    }
    .profile-header {
      background-color: #f8f9fa;
      border-radius: 10px;
      padding: 20px;
      margin-bottom: 30px;
    }
    .form-section {
      background-color: #ffffff;
      border-radius: 10px;
      padding: 30px;
      box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .has-error .help-block {
      color: #dc3545;
    }
    .form-label {
      font-weight: 600;
    }
    .btn-group-custom {
      margin-top: 20px;
    }
  </style>
</head>
<body>
  <div class="wrapper">
    <div class="profile-header text-center">
      <h2>Patient Profile</h2>
      <p class="lead">Manage your personal and medical information</p>
      <p class="text-muted">User ID: <?php echo $_SESSION["id"]; ?> | Email: <?php echo htmlspecialchars($_SESSION["email"]); ?></p>
    </div>

    <?php 
      if (!empty($success_message)) {
        echo '<div class="alert alert-success alert-dismissible fade show" role="alert">';
        echo htmlspecialchars($success_message);
        echo '<button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>';
        echo '</div>';
      }
    ?>

    <div class="form-section">
      <form action="<?php echo htmlspecialchars($_SERVER["PHP_SELF"]); ?>" method="post">

        <!-- Personal Information Section -->
        <h4 class="mb-3">Personal Information</h4>

        <div class="row">
          <div class="col-md-6">
            <div class="mb-3 <?php echo (!empty($name_err)) ? 'has-error' : ''; ?>">
              <label class="form-label">Full Name *</label>
              <input type="text" name="name" class="form-control" value="<?php echo htmlspecialchars($name); ?>" required>
              <span class="help-block"><?php echo $name_err; ?></span>
            </div>
          </div>
          <div class="col-md-6">
            <div class="mb-3">
              <label class="form-label">Email Address</label>
              <input type="email" class="form-control" value="<?php echo htmlspecialchars($email); ?>" disabled>
              <small class="text-muted">Email cannot be changed</small>
            </div>
          </div>
        </div>

        <div class="row">
          <div class="col-md-4">
            <div class="mb-3 <?php echo (!empty($age_err)) ? 'has-error' : ''; ?>">
              <label class="form-label">Age</label>
              <input type="number" name="age" class="form-control" value="<?php echo htmlspecialchars($age); ?>" min="0" max="150">
              <span class="help-block"><?php echo $age_err; ?></span>
            </div>
          </div>
          <div class="col-md-4">
            <div class="mb-3">
              <label class="form-label">Gender</label>
              <select name="gender" class="form-select">
                <option value="">Select Gender</option>
                <option value="Male" <?php echo ($gender == 'Male') ? 'selected' : ''; ?>>Male</option>
                <option value="Female" <?php echo ($gender == 'Female') ? 'selected' : ''; ?>>Female</option>
                <option value="Other" <?php echo ($gender == 'Other') ? 'selected' : ''; ?>>Other</option>
              </select>
            </div>
          </div>
          <div class="col-md-4">
            <div class="mb-3 <?php echo (!empty($phone_err)) ? 'has-error' : ''; ?>">
              <label class="form-label">Phone Number</label>
              <input type="tel" name="phone" class="form-control" value="<?php echo htmlspecialchars($phone); ?>">
              <span class="help-block"><?php echo $phone_err; ?></span>
            </div>
          </div>
        </div>

        <div class="mb-3">
          <label class="form-label">Address</label>
          <textarea name="address" class="form-control" rows="3" placeholder="Enter your full address"><?php echo htmlspecialchars($address); ?></textarea>
        </div>

        <!-- Medical Information Section -->
        <h4 class="mb-3 mt-4">Medical Information</h4>

        <div class="mb-3">
          <label class="form-label">Medical History & Surgical History</label>
          <textarea name="medical_history" class="form-control" rows="4" placeholder="Describe any past medical conditions, surgeries, or treatments"><?php echo htmlspecialchars($medical_history); ?></textarea>
          <small class="text-muted">Include relevant medical history & surgical history</small>
        </div>

        
        <div class="mb-3">
          <label class="form-label">Allergies & Medications</label>
          <textarea name="allergies" class="form-control" rows="3" placeholder="List known allergies (medications, foods, environmental)"><?php echo htmlspecialchars($allergies); ?></textarea>
        </div>

        <!-- Form Buttons -->
        <div class="btn-group-custom text-center">
          <button type="submit" class="btn btn-primary btn-lg">Update Profile</button>
          <a href="dashboard.php" class="btn btn-secondary btn-lg">Back to Dashboard</a>
        </div>
      </form>
    </div>

    <div class="text-center mt-4">
      <a href="logout.php" class="btn btn-danger">Sign Out</a>
    </div>
  </div>
</body>
</html>

    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>