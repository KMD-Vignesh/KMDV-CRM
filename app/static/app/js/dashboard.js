  document.addEventListener('DOMContentLoaded', function () {
    const ctx = document.getElementById('stockChart');
    if (!ctx) return;

    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: [{% for item in inventory_summary %}'{{ item.product__name }}'{% if not forloop.last %},{% endif %}{% endfor %}],
        datasets: [{
          label: 'Stock Quantity',
          data: [{% for item in inventory_summary %}{{ item.total }}{% if not forloop.last %},{% endif %}{% endfor %}],
          backgroundColor: 'rgba(52, 152, 219, 0.5)',
          borderColor: 'rgba(52, 152, 219, 1)',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: { y: { beginAtZero: true, title: { display: true, text: 'Units' } } }
      }
    });
  });