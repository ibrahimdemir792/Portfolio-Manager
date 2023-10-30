document.addEventListener("DOMContentLoaded", function () {
    // Toggle Dark Mode
    var themeToggle = document.getElementById("mySwitch");
    var htmlElement = document.querySelector("html");

    themeToggle.addEventListener("change", function() {
        if (themeToggle.checked)
        {
            htmlElement.setAttribute("data-bs-theme", "dark");
            localStorage.setItem("theme", "dark");
        }
        else
        {
            htmlElement.removeAttribute("data-bs-theme");
            localStorage.setItem("theme", "light");
        }
    });

    // Check preference for dark mode
    const themePreference = localStorage.getItem("theme");
    if (themePreference === "dark") {
        // Set dark mode
        themeToggle.checked = true;
        htmlElement.setAttribute("data-bs-theme", "dark");
    } else {
        // Set light mode
        themeToggle.checked = false;
        htmlElement.setAttribute("data-bs-theme", "light");
    };


    // To Show/Hide Charts Div
    const toggleButtons = document.querySelectorAll(".toggleButton");
    toggleButtons.forEach(function (button) {
        button.addEventListener("click", function () {
            const toggleId = button.getAttribute("data-toggle-id");
            const div = document.getElementById(toggleId);
            if (div.style.display === "none")
            {
                div.style.display = "block";
            }
            else
            {
                div.style.display = "none";
            }
        })
    });


    // Show/Hide Deposit/Withdraw Cash Window
    document.querySelector("#cashButton").onclick = function() {
        var div = document.getElementById("cashDiv");
        if (div.style.display === "none")
        {
            div.style.display = "block";
        }
        else
        {
            div.style.display = "none";
        }
    };


    // Dynamicly Change the Deposit or Withdraw Button
    const transactionType = document.getElementById("transactionType");
    const submitButton = document.getElementById("submitButton");

    transactionType.addEventListener("change", function() {
        if (transactionType.value === "Deposit")
        {
            submitButton.value = "Deposit";
        }
        else if (transactionType.value === "Withdraw")
        {
            submitButton.value = "Withdraw";
        }
    });


    // Prevent Submiting without Selecting Deposit/Withdraw Option
    document.getElementById("cashform").addEventListener("submit", function(event) {
        // Prevent the form from being submitted by default
        event.preventDefault();
        // Get the selected option from the select menu
        var selectedOption = document.getElementById("transactionType").value;
        // Check if an option has been selected
        if (selectedOption == "Select Transaction")
        {
            alert("Select Transaction Type");
        }
        else
        {
            this.submit();
        }
    });


    // Initalize DataTables for Sorting
    $(document).ready(function() {
        $('#sortable-table').DataTable({
            paging: false
        });
    });


    // Toggle Between Stock Details
    document.getElementById("properties").addEventListener("change", function() {
        var selectedOption = this.value;
        var propertyDetailsDivs = document.querySelectorAll(".property-details");

        propertyDetailsDivs.forEach(function(div) {
            if (div.id === selectedOption) {
                div.style.display = "block";
            } else {
                div.style.display = "none";
            }
        });
    });


});


