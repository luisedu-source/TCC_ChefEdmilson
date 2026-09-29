// Animação do header ao fazer scroll
window.addEventListener('scroll', function() {
  const header = document.querySelector('.topo');
  
  if (window.scrollY > 50) {
    header.classList.add('scrolled');
  } else {
    header.classList.remove('scrolled');
  }
});

const timelineObserver = new IntersectionObserver(function(entries) {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      const timelineItems = entry.target.querySelectorAll('.timeline-item');
      
      timelineItems.forEach((item, index) => {
        setTimeout(() => {
          item.classList.add('animate');
        }, index * 100);
      });
      
      timelineObserver.unobserve(entry.target);
    }
  });
}, { threshold: 0.2 });

const timelineSection = document.querySelector('.timeline-section');
if (timelineSection) {
  timelineObserver.observe(timelineSection);
}

// Funcionalidade do formulário de orçamento
document.addEventListener('DOMContentLoaded', function() {
  const orcamentoForm = document.getElementById('orcamentoForm');
  
  if (orcamentoForm) {
    // Formatação de telefone
    const telefonInput = document.getElementById('telefone');
    
    if (telefonInput) {
      telefonInput.addEventListener('input', function(e) {
        let valor = e.target.value.replace(/\D/g, ''); // Remove tudo que não é número
        
        if (valor.length > 11) {
          valor = valor.slice(0, 11); // Limita a 11 dígitos
        }
        
        // Formata no padrão (99) 99999-9999
        if (valor.length <= 2) {
          e.target.value = valor;
        } else if (valor.length <= 7) {
          e.target.value = `(${valor.slice(0, 2)}) ${valor.slice(2)}`;
        } else {
          e.target.value = `(${valor.slice(0, 2)}) ${valor.slice(2, 7)}-${valor.slice(7)}`;
        }
      });
    }
    
    // Formatação de CEP
    const cepInput = document.getElementById('cep');
    
    if (cepInput) {
      cepInput.addEventListener('input', function(e) {
        let valor = e.target.value.replace(/\D/g, ''); // Remove tudo que não é número
        
        if (valor.length > 8) {
          valor = valor.slice(0, 8); // Limita a 8 dígitos
        }
        
        // Formata no padrão 99999-999
        if (valor.length <= 5) {
          e.target.value = valor;
        } else {
          e.target.value = `${valor.slice(0, 5)}-${valor.slice(5)}`;
        }
      });
    }
    
    // Validação e envio do formulário
    orcamentoForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      // Validar campos obrigatórios
      const nome = document.getElementById('nome').value.trim();
      const email = document.getElementById('email').value.trim();
      const telefone = document.getElementById('telefone').value.trim();
      const convidados = document.getElementById('convidados').value;
      const tipoEvento = document.getElementById('tipoEvento').value;
      const dataEvento = document.getElementById('dataEvento').value;
      const tipoServico = document.getElementById('tipoServico').value;
      const privacidade = document.getElementById('privacidade').checked;
      
      if (!nome || !email || !telefone || !convidados || !tipoEvento || !dataEvento || !tipoServico || !privacidade) {
        alert('Por favor, preencha todos os campos obrigatórios e aceite a Política de Privacidade.');
        return;
      }
      
      // Validar email
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(email)) {
        alert('Por favor, insira um email válido.');
        return;
      }
      
      // Coletar dados do formulário
      const formData = new FormData(orcamentoForm);
      
      // Aqui você pode enviar os dados para o servidor
      console.log('Formulário validado e pronto para envio');
      console.log('Dados:', Object.fromEntries(formData));
      
      // Simular envio (você pode conectar a um endpoint real)
      alert('Obrigado! Receberemos sua solicitação em breve. Responderemos até 48 horas úteis.');
      orcamentoForm.reset();
    });
  }
});
