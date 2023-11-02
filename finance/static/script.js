document.addEventListener("DOMContentLoaded", function () {
    // Check the page title to determine which page you are on
    const pageTitle = document.title;
    
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

    if(pageTitle.includes("Portfolio")) {
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


        // Add an event listener to handle stock name link clicks
        const toggles = document.querySelectorAll(".toggleButton");
        toggles.forEach(function (button) {
            button.addEventListener("click", function () {
                const symbol = button.getAttribute("data-symbol");
                const chartName = button.getAttribute("data-chart-name");

                // Fetch data for the selected stock
                fetch(`/get_stock_data?symbol=${symbol}`)
                    .then(response => response.json())
                    .then(data => {
                        // Process the data and create the chart for the selected stock
                        // Use chartName to display the stock name in the chart
                        var chartId = `chart-${chartName}`;
                        var chartDom = document.getElementById(chartId);
                        if (chartDom) {
                            const myChart = echarts.init(chartDom);
                            // Process the data and create the chart
                            const dataArray = data.data;
                            const xAxisData = dataArray.map(item => {
                                const date = new Date(item.index);
                                return date.toLocaleDateString();   // Format as 'MM/DD/YYYY' or as needed
                            });

                            const yAxisData = dataArray.map(item => [item.open, item.close, item.low, item.high]);

                            const option = {
                                xAxis: {
                                    data: xAxisData,
                                },
                                yAxis: {},
                                series: [
                                    {
                                        type: 'candlestick',
                                        data: yAxisData,
                                    },
                                ],
                            };

                            // Set the option and render the chart
                            option && myChart.setOption(option);
                        } else {
                            console.error("Chart container not found:", chartId);
                        }
                    })
                    .catch(error => {
                        console.error('Error fetching data:', error);
                    });
            })
        });

    }


    if(pageTitle.includes("Quote")) {
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
    }


    if(pageTitle.includes("Sell")) {
        // Show share count on sell page
        const symbolSelect = document.getElementById("symbol-select");
        const sharesInfoDiv = document.getElementById("shares-info");
        const sharesCountSpan = document.getElementById("shares-number");
        const shareNameSpan = document.getElementById("share-name");
        
        symbolSelect.addEventListener("change", function() {
            const selectedOption = symbolSelect.options[symbolSelect.selectedIndex];
            const selectedShares = selectedOption.getAttribute("data-shares");
            const selectedName = selectedOption.getAttribute("data-name");

            sharesCountSpan.textContent = selectedShares;
            shareNameSpan.textContent = selectedName;
            sharesInfoDiv.style.display = "block";
        });
    }

    
    if(pageTitle.includes("Chart")) {
        var chartDom = document.getElementById('main');
        var myChart = echarts.init(chartDom);
        let option;

        fetch(`/get_stock_data?symbol=AAPL`)
            .then(response => response.json())
            .then(data => {
                // Process the data to format it for the chart
                const dataArray = data.data;
                const xAxisData = dataArray.map(item => {
                    const date = new Date(item.index);
                    return date.toLocaleDateString(); // Format as 'MM/DD/YYYY' or as needed
                });

                const yAxisData = dataArray.map(item => [item.open, item.close, item.low, item.high]);
        
                option = {
                    xAxis: {
                        data: xAxisData,
                    },
                    yAxis: {},
                    series: [
                        {
                            type: 'candlestick',
                            data: yAxisData,
                        },
                    ],
                };
        
                // Set the option and render the chart
                option && myChart.setOption(option);
            })
            .catch(error => {
                console.error('Error fetching data:', error);
            });
                
    }


    if (pageTitle.includes("Profile Settings")) {
        const checkbox = document.getElementById("checkbox");
        const deleteAccButton = document.getElementById("deleteAccButton");
        
        checkbox.addEventListener("change", function () {
            deleteAccButton.disabled = !checkbox.checked;
        });        
    }
    
    
});