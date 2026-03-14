EVALS = evals
BASELINE = baseline

.PHONY: grade report verify clean

grade:
	cd $(EVALS) && python grade.py $(BASELINE)

report:
	cd $(EVALS) && python report_gen.py $(BASELINE)/benchmark.json

verify:
	@missing=0; \
	for dir in $(EVALS)/$(BASELINE)/p3-*/; do \
		for cfg in with_skill without_skill; do \
			[ -f "$$dir$$cfg/output.yaml" ] || { echo "MISSING: $$dir$$cfg/output.yaml"; missing=$$((missing+1)); }; \
		done; \
	done; \
	echo "Missing files: $$missing"; \
	[ "$$missing" -eq 0 ] && echo "All eval outputs present."

clean:
	find $(EVALS) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -name '*.pyc' -delete 2>/dev/null; \
	echo "Cleaned."
