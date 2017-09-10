
testfiledirs=`ls -d */`

testfiles:
	@for tdir in $(testfiledirs) ; do \
		$(MAKE) testfiles -C $$tdir ; \
	done

clean:
	@for tdir in $(testfiledirs) ; do \
		$(MAKE) clean -C $$tdir ; \
	done

.PHONY: testfiles clean
