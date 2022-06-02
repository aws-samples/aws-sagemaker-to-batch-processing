## Scikit-learn ML processing jobs on AWS Graviton instances with AWS Batch

This repository contains a simple way to extend the default SageMaker container for SKLearn to be run via AWS Batch. This could be useful for those looking to leverage the power of Graviton2 instances, which are currently not avaialable for SageMaker instances. Graviton2, run on arm64 arch, can offer significant cost efficiencies compared to x86 arch based instances. Specifically, this demo uses the c6g instances to run a data processing task, typically compute intensive.

## Security

See [CONTRIBUTING](CONTRIBUTING.md#security-issue-notifications) for more information.

## License

This library is licensed under the MIT-0 License. See the LICENSE file.

