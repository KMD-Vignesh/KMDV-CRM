# utils.py
from typing import Any, Dict, Iterable


def chart_js_script(
    chart_id: str,
    summary: Iterable[Dict[str, Any]],
    *,
    label_key: str = "product__name",
    data_key: str = "total",
    dataset_label: str = "Quantity",
) -> str:
    labels = ", ".join(f"'{item[label_key]}'" for item in summary)
    data = ", ".join(str(item[data_key]) for item in summary)

    return f"""
document.addEventListener('DOMContentLoaded', function () {{
  const ctx = document.getElementById('{chart_id}');
  if (ctx) {{
    new Chart(ctx, {{
      type: 'bar',
      data: {{
        labels: [{labels}],
        datasets: [{{
          label: '{dataset_label}',
          data: [{data}],
          backgroundColor: 'rgba(52, 152, 219, 0.5)',
          borderColor: 'rgba(52, 152, 219, 1)',
          borderWidth: 1
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        scales: {{
          y: {{
            beginAtZero: true,
            title: {{ display: true, text: 'Units' }}
          }}
        }}
      }}
    }});
  }}
}});
"""

