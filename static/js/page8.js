
function switchTab(tab) {
  if (tab === 'monthly') {
    document.querySelector('.monthly-form').style.display = 'block';
    document.querySelector('.annual-form').style.display = 'none';
    document.getElementById('monthlyTab').classList.add('active');
    document.getElementById('annualTab').classList.remove('active');
  } else {
    document.querySelector('.monthly-form').style.display = 'none';
    document.querySelector('.annual-form').style.display = 'block';
    document.getElementById('monthlyTab').classList.remove('active');
    document.getElementById('annualTab').classList.add('active');
  }
}
    // Month dropdown logic (from your page8)
    const monthInput = document.getElementById('monthInput');
    const monthDropdown = document.getElementById('monthDropdown');
    monthInput.addEventListener('click', () => monthDropdown.classList.toggle('show'));
    monthDropdown.querySelectorAll('div').forEach(item => {
      item.addEventListener('click', () => {
        monthInput.value = item.textContent;
        monthDropdown.classList.remove('show');
      });
    });
    window.onclick = function(e) {
      if (!e.target.matches('#monthInput')) {
        monthDropdown.classList.remove('show');
      }
    }

    // Calculation logic
    function calculateConsumption(mode) {
      let usage, year, days;
      if (mode === 'monthly') {
        usage = parseFloat(document.querySelector('.monthly-form .input-box').value.trim());
        const monthName = document.getElementById("monthInput").value.trim();
        year = parseInt(document.querySelectorAll('.monthly-form .input-box')[1].value.trim());

        const months = {January:0, February:1, March:2, April:3, May:4, June:5, July:6, August:7, September:8, October:9, November:10, December:11};
        const monthNumber = months[monthName];
        if (monthNumber === undefined) return alert("Select a valid month");
        days = new Date(year, monthNumber + 1, 0).getDate();

      } else {
        usage = parseFloat(document.querySelector('.annual-form .input-box').value.trim());
        year = parseInt(document.querySelectorAll('.annual-form .input-box')[1].value.trim());
        days = (year % 4 === 0 && (year % 100 !== 0 || year % 400 === 0)) ? 366 : 365;
      }

      if (isNaN(usage) || usage <= 0) return alert("Enter valid usage");
      if (isNaN(year) || year < 1) return alert("Enter valid year");

      const perDay = usage / days;
      document.getElementById("result").innerHTML = `Energy consumption per day: ${perDay.toFixed(2)} kWh (1 unit = 1 kWh)`;
    }