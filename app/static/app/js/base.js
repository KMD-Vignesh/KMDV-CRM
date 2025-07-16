      document.addEventListener("DOMContentLoaded", () => {
        const links = document.querySelectorAll("nav a[href]");
        const current = window.location.pathname;

        links.forEach((link) => {
          const base = link.getAttribute("href").split("/")[1]; // e.g. "inventory"
          link.classList.toggle("active", current.startsWith("/" + base + "/"));
        });
      });

      document.addEventListener("DOMContentLoaded", function () {
        // Handle all messages with dismiss classes
        const messages = document.querySelectorAll(".alert");

        messages.forEach(function (message) {
          let duration = 3000; // default 30 seconds

          // Check for dismiss-X classes
          const classes = message.className.split(" ");
          classes.forEach(function (cls) {
            if (cls.startsWith("dismiss-")) {
              duration = parseInt(cls.replace("dismiss-", "")) * 1000;
            }
          });

          // Auto-hide after duration
          setTimeout(function () {
            if (message.parentElement) {
              message.style.transition = "opacity 0.5s ease-out";
              message.style.opacity = "0";
              setTimeout(function () {
                if (message.parentElement) {
                  message.remove();
                }
              }, 500);
            }
          }, duration);
        });
      });
