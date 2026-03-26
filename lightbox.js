(() => {
  function initLightbox() {
    const contentImages = Array.from(
      document.querySelectorAll('main img, .gallery img, .lead-image')
    ).filter((img) => !img.closest('.lightbox-overlay'));

    if (!contentImages.length) {
      return;
    }

    const overlay = document.createElement('div');
    overlay.className = 'lightbox-overlay';
    overlay.setAttribute('aria-hidden', 'true');
    overlay.innerHTML = `
      <button class="lightbox-close" type="button" aria-label="Close image">×</button>
      <img class="lightbox-image" alt="">
      <div class="lightbox-caption" aria-live="polite"></div>
    `;

    document.body.appendChild(overlay);

    const overlayImage = overlay.querySelector('.lightbox-image');
    const overlayCaption = overlay.querySelector('.lightbox-caption');
    const closeButton = overlay.querySelector('.lightbox-close');

    function closeLightbox() {
      overlay.classList.remove('open');
      overlay.setAttribute('aria-hidden', 'true');
      document.body.classList.remove('lightbox-open');
      overlayImage.removeAttribute('src');
      overlayImage.removeAttribute('srcset');
      overlayImage.removeAttribute('sizes');
    }

    function openLightbox(img) {
      overlayImage.src = img.currentSrc || img.src;
      if (img.srcset) {
        overlayImage.srcset = img.srcset;
      }
      if (img.sizes) {
        overlayImage.sizes = img.sizes;
      }
      overlayImage.alt = img.alt || '';
      overlayCaption.textContent = img.alt || '';
      overlay.classList.add('open');
      overlay.setAttribute('aria-hidden', 'false');
      document.body.classList.add('lightbox-open');
      closeButton.focus();
    }

    contentImages.forEach((img) => {
      img.classList.add('lightbox-target');
      img.setAttribute('tabindex', '0');
      img.setAttribute('role', 'button');
      img.setAttribute('aria-label', img.alt ? `View full-size image: ${img.alt}` : 'View full-size image');

      img.addEventListener('click', () => openLightbox(img));
      img.addEventListener('keydown', (event) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          openLightbox(img);
        }
      });
    });

    closeButton.addEventListener('click', closeLightbox);

    overlay.addEventListener('click', (event) => {
      if (event.target === overlay) {
        closeLightbox();
      }
    });

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && overlay.classList.contains('open')) {
        closeLightbox();
      }
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initLightbox);
  } else {
    initLightbox();
  }
})();
