# divide-et-impera

Büyük işleri parçalara bölen, her parçayı güvenle yapabilecek en ucuz modele dağıtan bir Claude Code skill'i. Kritik işleri yönetici modelin kendisi yazar. Diğer modellerden gelenler doğrulanır ve kullanıcıya raporlanır.

*A Claude Code skill that splits large tasks across Haiku, Sonnet and Opus by criticality. The orchestrator writes the critical work itself, verifies what comes back, and reports.*

## Nasıl çalışır?

| Rol | Model | Ne yapar |
|---|---|---|
| Yönetici | Oturumun modeli (Fable / Opus) | Plan, şartname, **kritik işler**, doğrulama, rapor |
| `dei-deputy` | Opus | İsteğe bağlı yardımcı yönetici: büyük bir iş kolunu yönetir |
| `dei-builder` | Sonnet | Kapsamlı ama kritik olmayan işler: şartnameye göre kod, test, dokümantasyon |
| `dei-scout` | Haiku | Basit ve izole işler: araştırma, kaynak toplama, ayrıştırma, küçük scriptler |

### Kritiklik testi

Aşağıdaki sorulardan herhangi birinin cevabı "evet" ise iş kritiktir:
1. **Geri alınamazlık:** Hatayı geri almak zor mu?
2. **Güvenlik:** Bir güvenlik sınırına dokunuyor mu?
3. **Etki alanı:** Hata çok kullanıcıyı ya da sistemi etkiler mi?
4. **Sessiz hata:** Hata fark edilmeden zarar verebilir mi?
5. **Temel:** Başka işler bunun üzerine mi kurulacak?
6. **Test edilemezlik:** Bu ortamda otomatik olarak doğrulanamıyor mu?

Emin olunamayan durumda iş kritik sayılır. Projeye özel kritik alanlar `CLAUDE.md` dosyasındaki `Critical in this project` başlığı altına eklenir. Örnek için `examples/CLAUDE.md` dosyasına bak.

### Oturum modeline göre davranış
- **Fable:** Kritik işi kendisi yazar. `balanced` modunda şartnameyi Fable yazar, kodu Opus yazar, Fable satır satır inceler.
- **Opus:** Kritik işi kendisi yazar.
- **Sonnet / Haiku:** Kritik işi şartnameyle birlikte bir Opus alt ajanına devreder ve sonucu inceler.

## Kurulum

### Bütün projeler için (kişisel)
```bash
git clone https://github.com/AtaJudge/divide-et-impera.git
mkdir -p ~/.claude/skills ~/.claude/agents
cp -r divide-et-impera/skills/divide-et-impera ~/.claude/skills/
cp divide-et-impera/agents/*.md ~/.claude/agents/
```

### Tek bir proje için
Aynı dosyaları projenin `.claude/skills/` ve `.claude/agents/` klasörlerine kopyala ve commit'le. Bulut oturumları (claude.ai/code) bu yolu kullanır.

## Kullanım
```
/divide-et-impera <görev>
/divide-et-impera balanced <görev>     # Fable oturumunda maliyet odaklı mod
```
Skill yalnızca elle çağrıldığında çalışır (`disable-model-invocation: true`). Böylece istenmeyen alt ajan maliyeti oluşmaz.

## Bilinen sınırlar ve notlar
- **Alt ajanlar iç içe en fazla 3 katman olabilir.** Sınır `CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH` ayarıyla değiştirilebilir. Bu yapı en fazla 2 katman kullanır: yönetici → yardımcı yönetici → işçi.
- **Model belirtilmeyen alt ajan, kendisini başlatan ajanın modelini kullanır.** Bu yüzden skill yalnızca modeli sabitlenmiş `dei-*` ajanlarını kullanır. Hangi ajanın hangi modelde çalıştığını `/tasks` ile kontrol edebilirsin.
- **`dei-scout` ajanının Bash erişimi var**, çünkü basit scriptler yazması gerekiyor. Ajan tanımı onu salt okumaya yönlendiriyor, ama bu araç seviyesinde bir zorunluluk değil. Daha sıkı bir kısıt istersen `settings.json` dosyasına `permissions.deny` kuralları ekle.
- **Fiyatlar** (yazıldığı tarihte, 1M token başına girdi/çıktı): Haiku 5.5 $0.10/$0.50 · Sonnet 5.5 $2/$10 · Opus 5.5 $4/$20 · Fable 5.2 $8/$40.
