PHASE3 = valid-guard-workspace/phase3
ITERATION = iteration-3

.PHONY: grade report verify clean

grade:
	cd $(PHASE3) && python grade_phase3.py $(ITERATION)

report:
	cd $(PHASE3) && python generate_report.py $(ITERATION)/benchmark.json

verify:
	@missing=0; \
	for dir in $(PHASE3)/$(ITERATION)/p3-*/; do \
		for cfg in with_skill without_skill; do \
			[ -f "$$dir$$cfg/output.yaml" ] || { echo "MISSING: $$dir$$cfg/output.yaml"; missing=$$((missing+1)); }; \
		done; \
	done; \
	echo "Missing files: $$missing"; \
	[ "$$missing" -eq 0 ] && echo "All eval outputs present."

clean:
	find $(PHASE3) -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null; \
	find . -name '*.pyc' -delete 2>/dev/null; \
	echo "Cleaned."
