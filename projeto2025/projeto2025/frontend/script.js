const API_URL = "http://127.0.0.1:5000";

// ==================== TEMA ====================
function alternarTema() {
    document.body.classList.toggle('dark');
    const modoAtual = document.body.classList.contains('dark') ? 'dark' : 'light';
    localStorage.setItem('tema', modoAtual);
}

window.onload = function() {
    const temaSalvo = localStorage.getItem('tema');
    if (temaSalvo === 'dark') document.body.classList.add('dark');

    // Carrega tarefas se estiver na página principal
    if (window.location.pathname.endsWith("index.html")) {
        carregarTarefas();
    }
};

// ==================== CADASTRO ====================
async function registrar() {
    const nome = document.getElementById('nomeCadastro').value;
    const email = document.getElementById('emailCadastro').value;
    const senha = document.getElementById('senhaCadastro').value;

    if (!nome || !email || !senha) {
        alert("Preencha todos os campos!");
        return;
    }

    const resp = await fetch(`${API_URL}/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ nome, email, senha })
    });

    const data = await resp.json();
    alert(data.mensagem || data.erro);

    if (resp.ok) {
        window.location.href = "login.html";
    }
}

// ==================== LOGIN ====================
async function login() {
    const email = document.getElementById('emailLogin').value;
    const senha = document.getElementById('senhaLogin').value;

    const resp = await fetch(`${API_URL}/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, senha })
    });

    const data = await resp.json();

    if (data.token) {
        localStorage.setItem("token", data.token);
        window.location.href = "index.html";
    } else {
        alert(data.erro || "Falha no login!");
    }
}

// ==================== LOGOUT ====================
function logout() {
    localStorage.removeItem("token");
    window.location.href = "login.html";
}

// ==================== TAREFAS ====================
async function carregarTarefas() {
    const token = localStorage.getItem("token");
    if (!token) return window.location.href = "login.html";

    const resp = await fetch(`${API_URL}/tarefas`, {
        headers: { Authorization: "Bearer " + token }
    });

    if (resp.status === 401) {
        alert("Sessão expirada! Faça login novamente.");
        logout();
        return;
    }

    const tarefas = await resp.json();
    const lista = document.getElementById("listaTarefas");
    lista.innerHTML = "";

    tarefas.forEach(t => {
        // Card da nota
        const card = document.createElement("div");
        card.classList.add("note-card", corAleatoria());
        if (t.concluida) card.classList.add("done");

        // Título da nota
        const titulo = document.createElement("span");
        titulo.textContent = t.titulo;

        // Botão de exclusão
        const btnDel = document.createElement("button");
        btnDel.textContent = "🗑️";
        btnDel.classList.add("delete-btn");
        btnDel.onclick = async (e) => {
            e.stopPropagation();
            await fetch(`${API_URL}/tarefas/${t.id}`, {
                method: "DELETE",
                headers: { Authorization: "Bearer " + token }
            });
            carregarTarefas();
        };

        // Marca como concluída ao clicar no card
        card.onclick = async () => {
            await fetch(`${API_URL}/tarefas/${t.id}`, {
                method: "PUT",
                headers: {
                    "Content-Type": "application/json",
                    Authorization: "Bearer " + token
                },
                body: JSON.stringify({ concluida: !t.concluida })
            });
            carregarTarefas();
        };

        card.appendChild(titulo);
        card.appendChild(btnDel);
        lista.appendChild(card);
    });
}

async function adicionarTarefa() {
    const titulo = document.getElementById("novaTarefa").value;
    const token = localStorage.getItem("token");
    if (!titulo.trim()) return alert("Digite um título!");

    await fetch(`${API_URL}/tarefas`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            Authorization: "Bearer " + token
        },
        body: JSON.stringify({ titulo })
    });

    document.getElementById("novaTarefa").value = "";
    carregarTarefas();
}

// ==================== FUNÇÃO DE CORES ====================
function corAleatoria() {
    const cores = ["note-yellow", "note-blue", "note-green", "note-pink", "note-orange", "note-purple"];
    return cores[Math.floor(Math.random() * cores.length)];
}
