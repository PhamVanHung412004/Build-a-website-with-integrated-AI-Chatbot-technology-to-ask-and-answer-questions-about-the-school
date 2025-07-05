// Mobile menu toggle
const menuToggle = document.getElementById('menuToggle');
const mainNav = document.getElementById('mainNav');
menuToggle && menuToggle.addEventListener('click', function() {
  mainNav.classList.toggle('open');
});

// Đóng menu khi click ngoài (mobile)
document.addEventListener('click', function(e) {
  if (mainNav && mainNav.classList.contains('open')) {
    if (!mainNav.contains(e.target) && !menuToggle.contains(e.target)) {
      mainNav.classList.remove('open');
    }
  }
});

// Search popup
const searchBtn = document.getElementById('searchBtn');
const searchInputWrapper = document.getElementById('searchInputWrapper');
const closeSearch = document.getElementById('closeSearch');
searchBtn && searchBtn.addEventListener('click', function(e) {
  e.stopPropagation();
  searchInputWrapper.style.display = 'flex';
  document.getElementById('searchInput').focus();
});
closeSearch && closeSearch.addEventListener('click', function() {
  searchInputWrapper.style.display = 'none';
});
document.addEventListener('click', function(e) {
  if (searchInputWrapper && searchInputWrapper.style.display === 'flex') {
    if (!searchInputWrapper.contains(e.target) && e.target !== searchBtn) {
      searchInputWrapper.style.display = 'none';
    }
  }
});
// Ngăn click trong input không đóng popup
searchInputWrapper && searchInputWrapper.addEventListener('click', function(e) {
  e.stopPropagation();
});

// Popup open/close
function openPopup(id) {
  // ...
}
function closePopup(id) {
  // ...
}

// Smooth scroll
function scrollToSection(id) {
  // ...
}

// Carousel alumni
function initAlumniCarousel() {
  // ...
}

// Popup đăng ký Hero
const openRegister = document.getElementById('openRegister');
const registerPopup = document.getElementById('registerPopup');
const closeRegister = document.getElementById('closeRegister');
openRegister && openRegister.addEventListener('click', function(e) {
  e.preventDefault();
  registerPopup.classList.add('active');
  document.body.style.overflow = 'hidden';
});
closeRegister && closeRegister.addEventListener('click', function() {
  registerPopup.classList.remove('active');
  document.body.style.overflow = '';
});
registerPopup && registerPopup.addEventListener('click', function(e) {
  if (e.target === registerPopup) {
    registerPopup.classList.remove('active');
    document.body.style.overflow = '';
  }
});
// Smooth scroll cho nút Tìm Hiểu
const scrollToAbout = document.getElementById('scrollToAbout');
scrollToAbout && scrollToAbout.addEventListener('click', function(e) {
  e.preventDefault();
  document.getElementById('about-program').scrollIntoView({ behavior: 'smooth' });
});

// Popup mô tả ngành
const programInfoBtns = document.querySelectorAll('.program-info-btn');
programInfoBtns.forEach(btn => {
  btn.addEventListener('click', function() {
    const major = btn.getAttribute('data-major');
    alert('Thông tin chi tiết ngành: ' + major);
  });
});
const closeMajorBtns = document.querySelectorAll('.close-popup[data-close]');
closeMajorBtns.forEach(btn => {
  btn.addEventListener('click', function() {
    const id = btn.getAttribute('data-close');
    const popup = document.getElementById(id);
    if (popup) {
      popup.classList.remove('active');
      document.body.style.overflow = '';
    }
  });
});
// Đóng popup khi click ngoài
['popup-design','popup-business','popup-it','popup-semicon'].forEach(id => {
  const popup = document.getElementById(id);
  if (popup) {
    popup.addEventListener('click', function(e) {
      if (e.target === popup) {
        popup.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }
});

// Alumni carousel (5 thẻ)
const alumniCarousel = document.getElementById('alumniCarousel');
const alumniCards = alumniCarousel ? Array.from(alumniCarousel.children) : [];
const alumniPrev = document.getElementById('alumniPrev');
const alumniNext = document.getElementById('alumniNext');
let alumniIndex = 0;
function getAlumniPerView() {
  if (window.innerWidth <= 600) return 1;
  if (window.innerWidth <= 900) return 2;
  return 5;
}
function showAlumni() {
  const perView = getAlumniPerView();
  alumniCards.forEach((card, i) => {
    if (i >= alumniIndex && i < alumniIndex + perView) {
      card.style.display = 'flex';
    } else {
      card.style.display = 'none';
    }
  });
}
function nextAlumni() {
  const perView = getAlumniPerView();
  alumniIndex = Math.min(alumniIndex + perView, alumniCards.length - perView);
  showAlumni();
}
function prevAlumni() {
  const perView = getAlumniPerView();
  alumniIndex = Math.max(alumniIndex - perView, 0);
  showAlumni();
}
alumniNext && alumniNext.addEventListener('click', nextAlumni);
alumniPrev && alumniPrev.addEventListener('click', prevAlumni);
window.addEventListener('resize', showAlumni);
showAlumni();
// Alumni popup
const alumniMoreBtns = document.querySelectorAll('.alumni-more-btn');
alumniMoreBtns.forEach(btn => {
  btn.addEventListener('click', function() {
    const alumni = btn.getAttribute('data-alumni');
    const popup = document.getElementById('popup-' + alumni);
    if (popup) {
      popup.classList.add('active');
      document.body.style.overflow = 'hidden';
    }
  });
});
['popup-thanh','popup-mai','popup-quyet'].forEach(id => {
  const popup = document.getElementById(id);
  if (popup) {
    popup.addEventListener('click', function(e) {
      if (e.target === popup) {
        popup.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }
});

// News popup
const newsMoreBtns = document.querySelectorAll('.news-more-btn');
newsMoreBtns.forEach(btn => {
  btn.addEventListener('click', function() {
    alert('Thông tin chi tiết tin tức sẽ được bổ sung sau!');
  });
});
['popup-chieusang','popup-hanhtrinh','popup-yakult'].forEach(id => {
  const popup = document.getElementById(id);
  if (popup) {
    popup.addEventListener('click', function(e) {
      if (e.target === popup) {
        popup.classList.remove('active');
        document.body.style.overflow = '';
      }
    });
  }
});

// Footer social icons
const socialLinks = {
  facebook: 'https://facebook.com/fptbtec',
  youtube: 'https://youtube.com',
  tiktok: 'https://tiktok.com',
};
document.querySelectorAll('.footer-icon').forEach(icon => {
  icon.addEventListener('click', function(e) {
    e.preventDefault();
    const type = icon.getAttribute('data-social');
    if (socialLinks[type]) {
      window.open(socialLinks[type], '_blank');
    }
  });
});

document.addEventListener('DOMContentLoaded', function() {
  // Khởi tạo các chức năng khi DOM sẵn sàng
  initAlumniCarousel();
});

// Dropdown menu hiện đại: click mới mở, click ra ngoài thì đóng
const dropdowns = document.querySelectorAll('.dropdown');
dropdowns.forEach(drop => {
  const toggle = drop.querySelector('.dropdown-toggle');
  toggle && toggle.addEventListener('click', function(e) {
    e.preventDefault();
    // Đóng tất cả dropdown khác
    dropdowns.forEach(d => { if (d !== drop) d.classList.remove('open'); });
    drop.classList.toggle('open');
  });
});
window.addEventListener('click', function(e) {
  dropdowns.forEach(drop => {
    if (!drop.contains(e.target)) {
      drop.classList.remove('open');
    }
  });
});

// Popup Liên hệ
const contactBtn = document.getElementById('contactBtn');
const contactPopup = document.getElementById('contactPopup');
const closeContact = document.getElementById('closeContact');
contactBtn && contactBtn.addEventListener('click', function(e) {
  e.preventDefault();
  contactPopup.classList.add('active');
  document.body.style.overflow = 'hidden';
});
closeContact && closeContact.addEventListener('click', function() {
  contactPopup.classList.remove('active');
  document.body.style.overflow = '';
});
contactPopup && contactPopup.addEventListener('click', function(e) {
  if (e.target === contactPopup) {
    contactPopup.classList.remove('active');
    document.body.style.overflow = '';
  }
});

// Bộ lọc ngành hot
const filterBtns = document.querySelectorAll('.filter-btn');
const programCards = document.querySelectorAll('.program-card');
filterBtns.forEach(btn => {
  btn.addEventListener('click', function() {
    filterBtns.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.getAttribute('data-filter');
    programCards.forEach(card => {
      if (filter === 'all') card.style.display = '';
      else if (filter === 'hot') card.classList.contains('hot') ? card.style.display = '' : card.style.display = 'none';
    });
  });
});

// Footer Đăng Ký Ngay mở popup
const footerRegisterBtn = document.getElementById('footerRegisterBtn');
footerRegisterBtn && footerRegisterBtn.addEventListener('click', function() {
  const popup = document.getElementById('registerPopup');
  if (popup) {
    popup.classList.add('active');
    document.body.style.overflow = 'hidden';
  }
});

// Newsletter form
const newsletterForm = document.getElementById('newsletterForm');
const newsletterSuccess = document.getElementById('newsletterSuccess');
newsletterForm && newsletterForm.addEventListener('submit', function(e) {
  e.preventDefault();
  newsletterSuccess.style.display = 'block';
  setTimeout(() => newsletterSuccess.style.display = 'none', 3000);
  newsletterForm.reset();
});

// Scroll to top
const scrollTopBtn = document.getElementById('scrollTopBtn');
scrollTopBtn && scrollTopBtn.addEventListener('click', function() {
  window.scrollTo({ top: 0, behavior: 'smooth' });
});

// HERO TYPEWRITER & POEM POPUP
const heroTypewriter = document.getElementById('heroTypewriter');
const heroPoem = [
  'Trạng Code ngồi bên cửa sổ,',
  'Nắng vàng rơi trên trang thơ,',
  'Mùa hè BTEC rực rỡ,',
  'Mở lối truyền thống, hiện đại hòa mơ.'
];
function typeWriterEffect(lines, el, speed = 45, lineDelay = 700) {
  let line = 0, char = 0;
  el.textContent = '';
  function typeLine() {
    if (line >= lines.length) return;
    if (char < lines[line].length) {
      el.textContent += lines[line][char];
      char++;
      setTimeout(typeLine, speed);
    } else {
      el.textContent += '\n';
      line++;
      char = 0;
      setTimeout(typeLine, lineDelay);
    }
  }
  typeLine();
}
if (heroTypewriter) {
  typeWriterEffect(heroPoem, heroTypewriter);
}
// Popup thơ Trạng Code
const openPoem = document.getElementById('openPoem');
const poemPopup = document.getElementById('poemPopup');
const closePoem = document.getElementById('closePoem');
openPoem && openPoem.addEventListener('click', function(e) {
  e.preventDefault();
  poemPopup.classList.add('active');
  document.body.style.overflow = 'hidden';
});
closePoem && closePoem.addEventListener('click', function() {
  poemPopup.classList.remove('active');
  document.body.style.overflow = '';
});
poemPopup && poemPopup.addEventListener('click', function(e) {
  if (e.target === poemPopup) {
    poemPopup.classList.remove('active');
    document.body.style.overflow = '';
  }
});

// Hiệu ứng mở menu mobile
const toggle = document.querySelector('.navbar-toggle');
const menu = document.querySelector('.navbar-menu');
if (toggle && menu) {
  toggle.addEventListener('click', () => {
    menu.style.display = menu.style.display === 'flex' ? 'none' : 'flex';
  });
}

// Filter ngành học
const filterBtns = document.querySelectorAll('.filter-btn');
filterBtns.forEach(btn => {
  btn.addEventListener('click', function() {
    filterBtns.forEach(b => b.classList.remove('active'));
    this.classList.add('active');
    // Lọc card ngành học ở đây nếu muốn
  });
});

// Popup chi tiết card
const cardBtns = document.querySelectorAll('.card-btn');
cardBtns.forEach(btn => {
  btn.addEventListener('click', function() {
    alert('Thông tin chi tiết sẽ được bổ sung sau!');
  });
});

// Alumni carousel (demo scroll)
const alumniCarouselEl = document.querySelector('.alumni-carousel');
if(alumniCarouselEl) {
  alumniCarouselEl.addEventListener('wheel', e => {
    alumniCarouselEl.scrollLeft += e.deltaY;
  });
}

// Scroll to top
const scrollBtn = document.querySelector('.scroll-top');
if(scrollBtn) {
  window.addEventListener('scroll', () => {
    scrollBtn.style.display = window.scrollY > 200 ? 'block' : 'none';
  });
} 