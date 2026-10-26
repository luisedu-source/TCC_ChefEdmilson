// Animação do header ao fazer scroll
window.addEventListener('scroll', function() {
  const header = document.querySelector('.topo');
  if (!header) return;

  if (window.scrollY > 50) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
});

const timelineSection = document.querySelector('.timeline-section');
if (timelineSection && 'IntersectionObserver' in window) {
  const timelineObserver = new IntersectionObserver(function(entries) {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.querySelectorAll('.timeline-item').forEach((item, index) => {
          setTimeout(() => item.classList.add('animate'), index * 100);
        });
        timelineObserver.unobserve(entry.target);
      }
    });
  }, { threshold: 0.2 });

  timelineObserver.observe(timelineSection);
}
