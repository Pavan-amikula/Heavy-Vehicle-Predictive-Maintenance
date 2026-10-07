        (function () {
            // 1. smooth scroll reveal (advanced intersection observer)
            const faders = document.querySelectorAll('.info-card, .feature-item, .section-title, .diagnostic-card');
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('visible');
                        entry.target.style.transition = 'opacity 0.7s cubic-bezier(0.2, 0.9, 0.1, 1), transform 0.8s cubic-bezier(0.2, 0.9, 0.1, 1)';
                    }
                });
            }, { threshold: 0.15, rootMargin: '0px 0px -50px 0px' });

            faders.forEach(el => {
                el.classList.add('js-fade');
                observer.observe(el);
            });

            // 2. interactive card demo (Optional/Legacy support)
            const cards = document.querySelectorAll('.info-card');
            cards.forEach((card, index) => {
                card.addEventListener('click', function (e) {
                    if (this.hasAttribute('data-no-click')) return;
                    // ... existing logic if needed ...
                });
            });

            // 3. Sensor Input Interactions
            const inputs = document.querySelectorAll('input, select, textarea');
            inputs.forEach(input => {
                input.addEventListener('focus', () => {
                    const group = input.closest('.sensor-input-group, .input-group');
                    if (group) {
                        group.style.transform = 'translateY(-5px)';
                        group.style.transition = 'all 0.3s cubic-bezier(0.2, 0.9, 0.1, 1)';
                    }
                });
                input.addEventListener('blur', () => {
                    const group = input.closest('.sensor-input-group, .input-group');
                    if (group) {
                        group.style.transform = 'translateY(0)';
                    }
                });
            });

            // 4. Logo Pulse
            const logoIcon = document.querySelector('.nav-logo i');
            if (logoIcon) {
                setInterval(() => {
                    logoIcon.style.textShadow = '0 0 15px #D83F6C, 0 0 5px #B75D69';
                    setTimeout(() => {
                        logoIcon.style.textShadow = '0 0 8px #D83F6C80';
                    }, 300);
                }, 4000);
            }
        })();
