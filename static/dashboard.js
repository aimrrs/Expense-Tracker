document.addEventListener('DOMContentLoaded', function() {
    // Initialize variables
    let expenseChart;
    let selectedMonth, selectedYear;
    let userEmail = '';
    
    // DOM Elements
    const dateSelector = document.getElementById('date-selector');
    const currentMonthEl = document.getElementById('current-month');
    const usernameEl = document.getElementById('username');
    const userAvatarEl = document.getElementById('user-avatar');
    const monthlyBudgetEl = document.getElementById('monthly-budget');
    const spentAmountEl = document.getElementById('spent-amount');
    const remainingAmountEl = document.getElementById('remaining-amount');
    const budgetPercentEl = document.getElementById('budget-percent');
    const progressBarEl = document.getElementById('progress-bar');
    const dailyBudgetEl = document.getElementById('daily-budget');
    const expenseBreakdownEl = document.getElementById('expense-breakdown');
    const transactionsListEl = document.getElementById('transactions-list');
    
    // Navigation elements
    const dashboardLink = document.querySelector('.main-nav li:nth-child(1)');
    const transactionsLink = document.getElementById('transactions-link');
    const analyticsLink = document.getElementById('analytics-link');
    const budgetLink = document.getElementById('budget-link');
    const settingsLink = document.getElementById('settings-link');
    
    // Sections
    const dashboardSection = document.querySelector('.charts-section').parentElement;
    const transactionsSection = document.querySelector('.transactions-section');
    
    // Modals
    const expenseModal = document.getElementById('expense-modal');
    const monthModal = document.getElementById('month-modal');
    const budgetModal = document.getElementById('budget-modal');
    const addExpenseBtn = document.getElementById('add-expense-btn');
    const expenseForm = document.getElementById('expense-form');
    const budgetForm = document.getElementById('budget-form');
    const closeModalBtns = document.querySelectorAll('.close-modal');
    
    // Month selector elements
    const currentYearEl = document.getElementById('current-year');
    const prevYearBtn = document.getElementById('prev-year');
    const nextYearBtn = document.getElementById('next-year');
    const monthBtns = document.querySelectorAll('.month-btn');
    
    // Initialize the dashboard
    initDashboard();
    
    // Event Listeners
    addExpenseBtn.addEventListener('click', openExpenseModal);
    expenseForm.addEventListener('submit', handleAddExpense);
    budgetForm.addEventListener('submit', handleSetBudget);
    dateSelector.addEventListener('click', openMonthModal);
    
    // Navigation event listeners
    transactionsLink.addEventListener('click', function(e) {
        e.preventDefault();
        showTransactions();
    });
    
    dashboardLink.addEventListener('click', function(e) {
        e.preventDefault();
        showDashboard();
    });
    
    budgetLink.addEventListener('click', function(e) {
        e.preventDefault();
        openBudgetModal();
    });
    
    closeModalBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            expenseModal.style.display = 'none';
            monthModal.style.display = 'none';
            budgetModal.style.display = 'none';
        });
    });
    
    // Close modal when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target === expenseModal) {
            expenseModal.style.display = 'none';
        }
        if (e.target === monthModal) {
            monthModal.style.display = 'none';
        }
        if (e.target === budgetModal) {
            budgetModal.style.display = 'none';
        }
    });
    
    // Tab switching for chart
    const tabButtons = document.querySelectorAll('.tab-btn');
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            tabButtons.forEach(btn => btn.classList.remove('active'));
            this.classList.add('active');
            updateChart(this.dataset.period);
        });
    });
    
    // Month selector events
    prevYearBtn.addEventListener('click', () => {
        currentYearEl.textContent = parseInt(currentYearEl.textContent) - 1;
    });
    
    nextYearBtn.addEventListener('click', () => {
        currentYearEl.textContent = parseInt(currentYearEl.textContent) + 1;
    });
    
    monthBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            const month = parseInt(btn.dataset.month);
            const year = parseInt(currentYearEl.textContent);
            selectMonth(month, year);
            monthModal.style.display = 'none';
        });
    });
    
    // Functions
    async function initDashboard() {
        // Set default date to today
        const today = new Date();
        document.getElementById('expense-date').valueAsDate = today;
        
        // Set current month and year
        selectedMonth = today.getMonth() + 1;
        selectedYear = today.getFullYear();
        updateMonthDisplay();
        
        // Initialize chart
        initChart();
        
        // Load dashboard data
        await loadDashboardData();
        
        // Load transactions
        await loadTransactions();
    }
    
    function showDashboard() {
        // Update navigation
        document.querySelectorAll('.main-nav li').forEach(li => li.classList.remove('active'));
        dashboardLink.classList.add('active');
        
        // Show dashboard, hide transactions
        transactionsSection.style.display = 'none';
        document.querySelector('.charts-section').style.display = 'grid';
        document.querySelector('.budget-cards').style.display = 'grid';
    }
    
    function showTransactions() {
        // Update navigation
        document.querySelectorAll('.main-nav li').forEach(li => li.classList.remove('active'));
        document.querySelector('.main-nav li:nth-child(2)').classList.add('active');
        
        // Show transactions, hide charts
        transactionsSection.style.display = 'block';
        document.querySelector('.charts-section').style.display = 'none';
    }
    
    async function loadDashboardData() {
        try {
            // Format the month for API request
            let monthStr = selectedMonth.toString().padStart(2, '0');
            let tableName = `m${monthStr}_${selectedYear}`;
            
            // Fetch monthly data
            const response = await fetch(`/api/monthly-data?month=${tableName}`);
            if (response.ok) {
                const data = await response.json();
                
                if (data.success) {
                    // Update budget cards
                    const totalExpense = data.totalExpense || 0;
                    const budget = data.budget || 1200; // Default budget if not set
                    const remaining = budget - totalExpense;
                    const percentUsed = Math.min(Math.round((totalExpense / budget) * 100), 100);
                    
                    monthlyBudgetEl.textContent = formatCurrency(budget);
                    spentAmountEl.textContent = formatCurrency(totalExpense);
                    remainingAmountEl.textContent = formatCurrency(remaining);
                    
                    // Update budget progress
                    budgetPercentEl.textContent = `${percentUsed}%`;
                    progressBarEl.style.width = `${percentUsed}%`;
                    
                    // Update daily budget
                    const daysInMonth = new Date(selectedYear, selectedMonth, 0).getDate();
                    const dailyBudget = remaining / daysInMonth;
                    dailyBudgetEl.textContent = formatCurrency(dailyBudget);
                    
                    // Update expense breakdown
                    if (data.categoryBreakdown && Object.keys(data.categoryBreakdown).length > 0) {
                        updateExpenseBreakdown(data.categoryBreakdown);
                    }
                    
                    // Update chart data
                    if (expenseChart && data.dailyExpenses) {
                        updateChartData(data.dailyExpenses);
                    }
                } else {
                    // No data for this month
                    resetDashboard();
                }
            }
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            resetDashboard();
        }
    }
    
    function resetDashboard() {
        monthlyBudgetEl.textContent = '$0.00';
        spentAmountEl.textContent = '$0.00';
        remainingAmountEl.textContent = '$0.00';
        budgetPercentEl.textContent = '0%';
        progressBarEl.style.width = '0%';
        dailyBudgetEl.textContent = '$0.00';
        expenseBreakdownEl.innerHTML = '<p>No expense data available</p>';
        
        if (expenseChart) {
            expenseChart.data.labels = [];
            expenseChart.data.datasets[0].data = [];
            expenseChart.update();
        }
    }
    
    async function loadTransactions() {
        try {
            // Format the month for API request
            let monthStr = selectedMonth.toString().padStart(2, '0');
            let tableName = `m${monthStr}_${selectedYear}`;
            
            // Fetch transactions
            const response = await fetch(`/api/transactions?month=${tableName}`);
            if (response.ok) {
                const data = await response.json();
                
                if (data.success && data.transactions && data.transactions.length > 0) {
                    displayTransactions(data.transactions);
                } else {
                    transactionsListEl.innerHTML = '<tr><td colspan="6" class="text-center">No transactions found</td></tr>';
                }
            }
        } catch (error) {
            console.error('Error loading transactions:', error);
            transactionsListEl.innerHTML = '<tr><td colspan="6" class="text-center">Error loading transactions</td></tr>';
        }
    }
    
    function displayTransactions(transactions) {
        transactionsListEl.innerHTML = '';
        
        transactions.forEach(transaction => {
            const row = document.createElement('tr');
            
            // Format date
            const date = new Date(transaction.edate);
            const formattedDate = `${date.getFullYear()}-${(date.getMonth() + 1).toString().padStart(2, '0')}-${date.getDate().toString().padStart(2, '0')}`;
            
            row.innerHTML = `
                <td>${transaction.ename}</td>
                <td>${formatCurrency(transaction.amount)}</td>
                <td>${transaction.category}</td>
                <td>${formattedDate}</td>
                <td>${transaction.description || 'N/A'}</td>
                <td>
                    <button class="action-btn edit-btn" data-id="${transaction.id}"><i class="fas fa-edit"></i></button>
                    <button class="action-btn delete-btn" data-id="${transaction.id}"><i class="fas fa-trash"></i></button>
                </td>
            `;
            
            transactionsListEl.appendChild(row);
        });
        
        // Add event listeners for edit and delete buttons
        document.querySelectorAll('.edit-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                // Implement edit functionality
                alert('Edit functionality to be implemented');
            });
        });
        
        document.querySelectorAll('.delete-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const id = this.dataset.id;
                if (confirm('Are you sure you want to delete this expense?')) {
                    deleteExpense(id);
                }
            });
        });
    }
    
    async function deleteExpense(id) {
        try {
            const response = await fetch(`/api/delete-expense?id=${id}`, {
                method: 'DELETE'
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Reload transactions and dashboard data
                    await loadTransactions();
                    await loadDashboardData();
                } else {
                    alert('Error deleting expense: ' + data.message);
                }
            }
        } catch (error) {
            console.error('Error deleting expense:', error);
            alert('Error deleting expense');
        }
    }
    
    function updateExpenseBreakdown(categoryData) {
        const breakdownContainer = document.createElement('div');
        breakdownContainer.className = 'breakdown-container';
        
        for (const [category, amount] of Object.entries(categoryData)) {
            const item = document.createElement('div');
            item.className = 'breakdown-item';
            
            // Determine color based on category
            let color = '#6b7280'; // Default gray
            if (category.toLowerCase().includes('food')) color = '#3b82f6';
            else if (category.toLowerCase().includes('education')) color = '#22c55e';
            else if (category.toLowerCase().includes('entertainment')) color = '#f59e0b';
            else if (category.toLowerCase().includes('shopping')) color = '#ef4444';
            else if (category.toLowerCase().includes('transport')) color = '#8b5cf6';
            
            item.innerHTML = `
                <div class="category-info">
                    <div class="category-color" style="background-color: ${color}"></div>
                    <div class="category-name">${category}</div>
                </div>
                <div class="category-amount">${formatCurrency(amount)}</div>
            `;
            breakdownContainer.appendChild(item);
        }
        
        expenseBreakdownEl.innerHTML = '';
        expenseBreakdownEl.appendChild(breakdownContainer);
    }
    
    function initChart() {
        const ctx = document.getElementById('expense-chart').getContext('2d');
        
        expenseChart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Daily Expenses',
                    data: [],
                    borderColor: '#3b82f6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4,
                    pointRadius: 4,
                    pointBackgroundColor: '#3b82f6',
                    pointBorderColor: '#fff',
                    pointBorderWidth: 2,
                    fill: false
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.05)',
                            drawBorder: false
                        },
                        ticks: {
                            callback: function(value) {
                                return '$' + value;
                            }
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    },
                    tooltip: {
                        backgroundColor: '#1a1f36',
                        titleColor: '#fff',
                        bodyColor: '#fff',
                        padding: 10,
                        displayColors: false,
                        callbacks: {
                            label: function(context) {
                                return '$' + context.parsed.y;
                            }
                        }
                    }
                }
            }
        });
    }
    
    function updateChartData(dailyExpenses) {
        const days = Object.keys(dailyExpenses).sort((a, b) => parseInt(a) - parseInt(b));
        const values = days.map(day => dailyExpenses[day]);
        
        expenseChart.data.labels = days;
        expenseChart.data.datasets[0].data = values;
        expenseChart.update();
    }
    
    function updateChart(period) {
        // This would fetch data for different time periods (week, month, year)
        console.log(`Updating chart for period: ${period}`);
        // For now, we'll just reload the current data
        loadDashboardData();
    }
    
    function openExpenseModal() {
        // Set default date to today if not already set
        if (!document.getElementById('expense-date').value) {
            document.getElementById('expense-date').valueAsDate = new Date();
        }
        expenseModal.style.display = 'flex';
    }
    
    function openBudgetModal() {
        // Get current budget value and set it in the form
        const currentBudget = parseFloat(monthlyBudgetEl.textContent.replace(/[^0-9.-]+/g, '')) || 0;
        document.getElementById('budget-amount').value = currentBudget;
        budgetModal.style.display = 'flex';
    }
    
    function openMonthModal() {
        // Set current year in the modal
        currentYearEl.textContent = selectedYear;
        
        // Highlight the selected month
        monthBtns.forEach(btn => {
            btn.classList.remove('active');
            if (parseInt(btn.dataset.month) === selectedMonth) {
                btn.classList.add('active');
            }
        });
        
        monthModal.style.display = 'flex';
    }
    
    async function handleAddExpense(e) {
        e.preventDefault();
        
        const name = document.getElementById('expense-name').value;
        const amount = document.getElementById('expense-amount').value;
        const category = document.getElementById('expense-category').value;
        const date = document.getElementById('expense-date').value;
        const description = document.getElementById('expense-description').value || 'Null';
        
        try {
            const response = await fetch('/api/add-expense', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    name: name,
                    amount: amount,
                    category: category,
                    date: date,
                    description: description
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Reset form and close modal
                    expenseForm.reset();
                    expenseModal.style.display = 'none';
                    
                    // Set default date to today
                    document.getElementById('expense-date').valueAsDate = new Date();
                    
                    // Reload dashboard data and transactions
                    await loadDashboardData();
                    await loadTransactions();
                } else {
                    alert('Error adding expense: ' + data.message);
                }
            }
        } catch (error) {
            console.error('Error adding expense:', error);
            alert('Error adding expense');
        }
    }
    
    async function handleSetBudget(e) {
        e.preventDefault();
        
        const budgetAmount = document.getElementById('budget-amount').value;
        
        try {
            const response = await fetch('/api/set-budget', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    amount: budgetAmount,
                    month: selectedMonth,
                    year: selectedYear
                })
            });
            
            if (response.ok) {
                const data = await response.json();
                if (data.success) {
                    // Close modal
                    budgetModal.style.display = 'none';
                    
                    // Reload dashboard data
                    await loadDashboardData();
                } else {
                    alert('Error setting budget: ' + data.message);
                }
            }
        } catch (error) {
            console.error('Error setting budget:', error);
            alert('Error setting budget');
        }
    }
    
    function selectMonth(month, year) {
        // Update selected month and year
        selectedMonth = month;
        selectedYear = year;
        
        // Update month display
        updateMonthDisplay();
        
        // Reload dashboard data and transactions
        loadDashboardData();
        loadTransactions();
    }
    
    function updateMonthDisplay() {
        const monthNames = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ];
        
        currentMonthEl.textContent = `${monthNames[selectedMonth - 1]} ${selectedYear}`;
    }
    
    function formatCurrency(amount) {
        return '$' + parseFloat(amount).toFixed(2).replace(/\d(?=(\d{3})+\.)/g, '$&,');
    }
});