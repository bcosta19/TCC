import sys
import unittest
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "webscrap"))

from scraper import is_session_expired, parse_vagas


class ScraperTests(unittest.TestCase):
    def test_vacancies_are_preserved_by_course(self):
        html = """
        <div class="card">
          <h5>Vagas Alocadas</h5>
          <table>
            <tr><th>Curso</th><th>Reg.</th><th>Vest.</th><th>Reg.</th><th>Vest.</th></tr>
            <tr><td>083 - Sistemas de Informação</td><td>30</td><td>1</td><td>29</td><td>1</td></tr>
            <tr><td>031 - Ciência da Computação</td><td>5</td><td>0</td><td>4</td><td>0</td></tr>
          </table>
        </div>
        """
        result = parse_vagas(BeautifulSoup(html, "html.parser"))
        self.assertEqual(result["vagas"], 36)
        self.assertEqual(result["inscritos"], 34)
        self.assertEqual(result["vagas_por_curso"][0]["codigo_curso"], "83")
        self.assertEqual(result["vagas_por_curso"][0]["vagas"], 31)

    def test_public_detail_with_login_link_is_not_expired(self):
        html = (
            '<a href="/graduacao/quadrodehorarios/sessions/new">Login</a>'
            "<h5>Vagas Alocadas</h5><h5>Horários da Turma</h5>"
        )
        self.assertFalse(is_session_expired(html))


if __name__ == "__main__":
    unittest.main()
