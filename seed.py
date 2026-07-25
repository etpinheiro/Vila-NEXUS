import os
import shutil
from app import create_app, db
from app.models import User, Company, CompanyRegistrationRequest, Property, PropertyImage, Favorite, VisitRequest

app = create_app()

def run_seed():
    with app.app_context():
        print("Re-criando tabelas do banco de dados (SQLite local / SQL Server ready)...")
        db.drop_all()
        db.create_all()

        print("Povoando dados iniciais para Vila dos Cabanos (Barcarena - PA)...")

        # 1. Usuário Administrador
        admin_user = User(
            name="Administrador System",
            email="admin@vilanexus.com.br",
            phone="(91) 99999-0000",
            role="admin",
            status="active"
        )
        admin_user.set_password("admin123")
        db.session.add(admin_user)

        # 2. Empresas Pré-Aprovadas
        comp1 = Company(
            name="Imobiliária Cabanos Prime",
            cnpj_cpf="12.345.678/0001-90",
            business_type="Imobiliária",
            phone="(91) 98111-2233",
            whatsapp="(91) 98111-2233",
            email="contato@cabanosprime.com.br",
            neighborhood="Vila dos Cabanos",
            address="Av. Cônego Batista Campos, nº 250",
            description="Líder em aluguel residencial e corporativo em Vila dos Cabanos e Barcarena.",
            is_approved=True
        )

        comp2 = Company(
            name="Pousada Sol & Mar Barcarena",
            cnpj_cpf="98.765.432/0001-10",
            business_type="Pousada",
            phone="(91) 98444-5566",
            whatsapp="(91) 98444-5566",
            email="reserva@pousadasolmar.com.br",
            neighborhood="Praia do Caripi",
            address="Av. Beira Mar, s/nº - Caripi",
            description="Pousada à beira-mar com suítes climatizadas, café da manhã regional e área de lazer.",
            is_approved=True
        )

        comp3 = Company(
            name="Barcarena Imóveis & Terrenos",
            cnpj_cpf="45.678.901/0001-23",
            business_type="Imobiliária",
            phone="(91) 98888-7766",
            whatsapp="(91) 98888-7766",
            email="vendas@barcarenaimoveis.com.br",
            neighborhood="Novo Paraíso",
            address="Rua Germano Aranha, nº 88",
            description="Especialistas em vendas de imóveis residenciais e áreas industriais.",
            is_approved=True
        )

        db.session.add_all([comp1, comp2, comp3])
        db.session.flush()

        # 3. Usuários Empresários Vinculados
        emp_user1 = User(
            name="Carlos Eduardo (Cabanos Prime)",
            email="carlos@cabanosprime.com.br",
            phone="(91) 98111-2233",
            role="entrepreneur",
            status="active",
            company_id=comp1.id
        )
        emp_user1.set_password("empresa123")

        emp_user2 = User(
            name="Juliana Costa (Sol & Mar)",
            email="juliana@pousadasolmar.com.br",
            phone="(91) 98444-5566",
            role="entrepreneur",
            status="active",
            company_id=comp2.id
        )
        emp_user2.set_password("empresa123")

        # 4. Usuário Cliente Demonstrativo
        client_user = User(
            name="Fernanda Lima (Cliente)",
            email="fernanda@gmail.com",
            phone="(91) 99333-4455",
            role="client",
            status="active"
        )
        client_user.set_password("cliente123")

        db.session.add_all([emp_user1, emp_user2, client_user])

        # 5. Solicitações Comerciais Pendentes (Fluxo de Lead de Empresário)
        req1 = CompanyRegistrationRequest(
            company_name="Amazonia Real Estate & Flat Services",
            contact_person="Roberto Silva",
            cnpj_cpf="33.444.555/0001-66",
            business_type="Imobiliária",
            phone="(91) 99123-4567",
            whatsapp="(91) 99123-4567",
            email="roberto@amazoniaflats.com.br",
            notes="Possuímos 15 flats totalmente mobiliados em Vila dos Cabanos prontos para locação de executivos de indústrias.",
            status="pending"
        )

        req2 = CompanyRegistrationRequest(
            company_name="Pousada & Hotel Beira Rio",
            contact_person="Mariana Souza",
            cnpj_cpf="55.666.777/0001-88",
            business_type="Hotel",
            phone="(91) 99876-5432",
            whatsapp="(91) 99876-5432",
            email="mariana@hotelbeirario.com.br",
            notes="Hotel com 30 suítes executivas e auditório para eventos em Barcarena.",
            status="pending"
        )

        db.session.add_all([req1, req2])

        # 6. Imóveis de Exemplo em Vila dos Cabanos
        p1 = Property(
            title="Casa Residencial 3 Quartos com Piscina e Varanda Gourmet",
            purpose="Venda",
            property_type="Casa",
            price=480000.00,
            neighborhood="Vila dos Cabanos",
            address="Rua Sete de Setembro, nº 142 - Vila dos Cabanos",
            description="Excelente casa com acabamento de alto padrão em Vila dos Cabanos. Possui 3 quartos sendo 1 suíte master com closet, sala ampla em 2 ambientes, cozinha planejada, varanda gourmet com churrasqueira e piscina privativa. Garagem coberta para 2 carros. Próxima a supermercados, farmácias e escolas.",
            bedrooms=3,
            bathrooms=3,
            suites=1,
            parking_spaces=2,
            area_sqm=180.0,
            features="Piscina, Churrasqueira, Varanda Gourmet, Ar Condicionado, Garagem Coberta, Portão Eletrônico, Móveis Planejados",
            company_id=comp1.id,
            phone="(91) 98111-2233",
            email="contato@cabanosprime.com.br",
            status="disponivel",
            is_highlighted=True,
            views_count=142
        )

        p2 = Property(
            title="Apartamento Executivo 2 Quartos Mobiliado para Aluguel Mensal",
            purpose="Aluguel",
            property_type="Apartamento",
            price=3200.00,
            neighborhood="Vila dos Cabanos",
            address="Av. D. Pedro II, Edifício Cabanos Tower, Apto 402",
            description="Apartamento 100% mobiliado ideal para executivos e profissionais das indústrias de Barcarena. Conta com 2 quartos climatizados, sala com Smart TV, cozinha equipada com eletrodomésticos, área de serviço e varanda ventilada. Condomínio fechado com portaria 24 horas e elevador.",
            bedrooms=2,
            bathrooms=2,
            suites=1,
            parking_spaces=1,
            area_sqm=75.0,
            features="100% Mobiliado, Ar Condicionado, Elevador, Portaria 24h, Wi-Fi Incluso, Garagem, Varanda",
            company_id=comp1.id,
            phone="(91) 98111-2233",
            email="contato@cabanosprime.com.br",
            status="disponivel",
            is_highlighted=True,
            views_count=210
        )

        p3 = Property(
            title="Suíte Vista Mar na Pousada Sol & Mar - Diária de Temporada",
            purpose="Hospedagem",
            property_type="Pousada/Quarto",
            price=280.00,
            neighborhood="Praia do Caripi",
            address="Av. Beira Mar, s/nº - Orla da Praia do Caripi",
            description="Hospede-se na melhor localização da Praia do Caripi! Suíte luxo com cama queen size, ar condicionado split, frigobar, TV a cabo e varanda privativa com vista panorâmica para a praia. Diária inclui café da manhã regional completo com sucos de frutas locais e tapiocas feitas na hora.",
            bedrooms=1,
            bathrooms=1,
            suites=1,
            parking_spaces=1,
            area_sqm=32.0,
            features="Frente para o Mar, Café da Manhã Incluso, Ar Condicionado, Frigobar, Wi-Fi, Estacionamento Privativo",
            company_id=comp2.id,
            phone="(91) 98444-5566",
            email="reserva@pousadasolmar.com.br",
            status="disponivel",
            is_highlighted=True,
            views_count=350
        )

        p4 = Property(
            title="Terreno Comercial 500m² em Localização Estratégica",
            purpose="Venda",
            property_type="Terreno",
            price=220000.00,
            neighborhood="Novo Paraíso",
            address="Rua Germano Aranha, s/nº",
            description="Terreno totalmente plano e escriturado medindo 15m x 33m (500m²) em rua pavimentada e com infraestrutura completa de água e luz. Excelente investimento para construção de galpão comercial, pousada ou vila de kitnets para locação.",
            bedrooms=0,
            bathrooms=0,
            suites=0,
            parking_spaces=0,
            area_sqm=500.0,
            features="Terreno Plano, Escriturado, Rua Pavimentada, Rede de Água, Energia Elétrica",
            company_id=comp3.id,
            phone="(91) 98888-7766",
            email="vendas@barcarenaimoveis.com.br",
            status="disponivel",
            is_highlighted=False,
            views_count=85
        )

        # Imóveis extras para garantir que toda combinação de filtro (finalidade x tipo)
        # tenha pelo menos um resultado de exemplo.
        p5 = Property(
            title="Casa de Temporada Beira-Mar no Caripi",
            purpose="Temporada",
            property_type="Casa",
            price=350.00,
            neighborhood="Praia do Caripi",
            address="Travessa da Orla, nº 45 - Praia do Caripi",
            description="Casa de temporada a 100m da praia, ideal para famílias e grupos. 3 quartos, cozinha completa, área externa com rede e churrasqueira. Diária com taxa de limpeza inclusa.",
            bedrooms=3,
            bathrooms=2,
            suites=1,
            parking_spaces=2,
            area_sqm=140.0,
            features="Perto da Praia, Churrasqueira, Rede, Cozinha Completa, Wi-Fi, Ventilador de Teto",
            company_id=comp2.id,
            phone="(91) 98444-5566",
            email="reserva@pousadasolmar.com.br",
            status="disponivel",
            is_highlighted=True,
            views_count=97
        )

        p6 = Property(
            title="Suíte Hotel Executiva com Café da Manhã - Centro",
            purpose="Hospedagem",
            property_type="Hotel/Suíte",
            price=210.00,
            neighborhood="Centro Barcarena",
            address="Av. Barão do Rio Branco, nº 310 - Centro",
            description="Suíte executiva no coração de Barcarena, próxima ao comércio e à sede das indústrias. Ar condicionado, frigobar, TV a cabo, Wi-Fi de alta velocidade e café da manhã incluso.",
            bedrooms=1,
            bathrooms=1,
            suites=1,
            parking_spaces=1,
            area_sqm=28.0,
            features="Café da Manhã Incluso, Ar Condicionado, Frigobar, Wi-Fi, Estacionamento",
            company_id=comp2.id,
            phone="(91) 98444-5566",
            email="reserva@pousadasolmar.com.br",
            status="disponivel",
            is_highlighted=False,
            views_count=64
        )

        p7 = Property(
            title="Galpão Comercial 300m² no Distrito Industrial",
            purpose="Venda",
            property_type="Galpão/Comercial",
            price=590000.00,
            neighborhood="Distrito Industrial",
            address="Rodovia Barcarena-Murucupi, Km 8 - Distrito Industrial",
            description="Galpão comercial com pé direito alto, ideal para logística ou pequena indústria. Área de escritório anexa, pátio para manobra de caminhões e portão eletrônico.",
            bedrooms=0,
            bathrooms=1,
            suites=0,
            parking_spaces=6,
            area_sqm=300.0,
            features="Pé Direito Alto, Pátio de Manobra, Escritório Anexo, Portão Eletrônico",
            company_id=comp3.id,
            phone="(91) 98888-7766",
            email="vendas@barcarenaimoveis.com.br",
            status="disponivel",
            is_highlighted=False,
            views_count=41
        )

        p8 = Property(
            title="Apartamento Compacto 1 Quarto para Aluguel - Centro",
            purpose="Aluguel",
            property_type="Apartamento",
            price=1350.00,
            neighborhood="Centro Barcarena",
            address="Rua Quinze de Novembro, nº 77 - Centro",
            description="Apartamento compacto e bem localizado, ótimo para solteiros ou casais. Próximo a bancos, farmácias e transporte público.",
            bedrooms=1,
            bathrooms=1,
            suites=0,
            parking_spaces=1,
            area_sqm=42.0,
            features="Próximo ao Centro, Portaria, Elevador",
            company_id=comp1.id,
            phone="(91) 98111-2233",
            email="contato@cabanosprime.com.br",
            status="disponivel",
            is_highlighted=False,
            views_count=58
        )

        db.session.add_all([p1, p2, p3, p4, p5, p6, p7, p8])
        db.session.flush()

        # Adicionar imagens placeholder para os imóveis de teste
        for p in [p1, p2, p3, p4, p5, p6, p7, p8]:
            img = PropertyImage(
                property_id=p.id,
                filename="property_placeholder.svg",
                is_primary=True,
                order=0
            )
            db.session.add(img)

        # Adicionar 1 favorito de demonstração
        fav = Favorite(user_id=client_user.id, property_id=p1.id)
        db.session.add(fav)

        db.session.commit()

        print("\n=========================================================================")
        print(" BANCO DE DADOS POVOADO COM SUCESSO PARA VILA DOS CABANOS!")
        print("=========================================================================")
        print(" CONTAS DE TESTE DISPONÍVEIS:")
        print(" -----------------------------------------------------------------------")
        print(" 1. ADMINISTRADOR GERAL:")
        print("    Email: admin@vilanexus.com.br | Senha: admin123")
        print(" 2. EMPRESÁRIO (Imobiliária Cabanos Prime):")
        print("    Email: carlos@cabanosprime.com.br | Senha: empresa123")
        print(" 3. EMPRESÁRIO (Pousada Sol & Mar):")
        print("    Email: juliana@pousadasolmar.com.br | Senha: empresa123")
        print(" 4. CLIENTE VISITANTE:")
        print("    Email: fernanda@gmail.com | Senha: cliente123")
        print("=========================================================================\n")

if __name__ == '__main__':
    run_seed()
