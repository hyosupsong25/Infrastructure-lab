# Terraform
코드를 통해 인프라를 관리할 수 있게 하는 오픈소스 툴

### Terraform Workflow
#### Write -> Plan -> Apply
테라폼의 워크 플로우는 Write -> Plan -> Apply 이며 각각의 과정은 아래와 같다
##### Write
Write 단계는 코드를 작성하는 것처럼 Terraform 구성을 작성하는 것이다.
이 단계에는 provider, resource 등이 생성되고 해당 코드는 HCL(Hashicorp Configuration Language)를 통해 작성되고 .tf 확장자를 갖는다.


##### Plan
Plan 단계는 Write 단계에서 작성된 코드가 적용 가능한지, 어떤 것들이 변경되는지 Apply 전에 확인하는 단계이다.

##### Apply
Apply 단계는 Plan을 통해 확인한 인프라 생성 및 변경사항들을 실제로 프로비저닝 하는 단계이다.
