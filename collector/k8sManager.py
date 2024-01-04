from kubernetes import client, config
from time import sleep


class K8sManager:
    def __init__(self, namespace):
        # Load the Kubernetes configuration
        config.load_kube_config()

        # Create the Kubernetes API client
        self.api_client_corev1 = client.CoreV1Api()
        self.api_client_appsv1 = client.AppsV1Api()
        self.namespace = namespace

        self.pod_list = self.api_client_corev1.list_namespaced_pod(
            namespace=self.namespace)
        self.service_list = self.api_client_corev1.list_namespaced_service(
            namespace=self.namespace)
        self.deployment_list = self.api_client_appsv1.list_namespaced_deployment(
            namespace=self.namespace)

    # Update the list of pods, services, and deployments
    def update(self):
        self.pod_list = self.api_client_corev1.list_namespaced_pod(
            namespace=self.namespace)
        self.service_list = self.api_client_corev1.list_namespaced_service(
            namespace=self.namespace)
        self.deployment_list = self.api_client_appsv1.list_namespaced_deployment(
            namespace=self.namespace)

    # Get the list of pods' name
    def get_pods_name_list(self):
        return [pod.metadata.name for pod in self.pod_list.items]

    # Get the list of services' name
    def scale_deployment(self, deployment_name, replica_num):
        deployment = self.api_client_appsv1.read_namespaced_deployment(
            deployment_name, self.namespace)
        if deployment.spec.replicas != replica_num:
            deployment.spec.replicas = replica_num
            self.api_client_appsv1.patch_namespaced_deployment_scale(
                    name=deployment_name, namespace=self.namespace, body=deployment)
            # Wait for the deployment to finish
            while True:
                deployment = self.api_client_appsv1.read_namespaced_deployment(
                    deployment_name, self.namespace)
                # Check if all replicas are available and the rollout is complete
                if (
                    deployment.status.available_replicas == deployment.spec.replicas
                    and deployment.status.replicas == deployment.spec.replicas
                    and deployment.status.updated_replicas == deployment.spec.replicas
                ):
                    break
            print(
                f"[K8sManager Scale] Scale {deployment_name} to {replica_num} pods.")
            sleep(2.5)
        else:
            print(
                f"[K8sManager Scale] Keep {deployment_name} have {replica_num} pods.")

    def set_limit(self, deployment_name, cpu_limit, mem_limit):
        deployment = self.api_client_appsv1.read_namespaced_deployment(
            deployment_name, self.namespace)
        if deployment.spec.template.spec.containers[0].resources.limits:
            old_cpu_limit = deployment.spec.template.spec.containers[0].resources.limits["cpu"]
            deployment.spec.template.spec.containers[0].resources.limits["cpu"] = f"{cpu_limit}m"
            old_memory_limit = deployment.spec.template.spec.containers[0].resources.limits["memory"]
            deployment.spec.template.spec.containers[0].resources.limits["memory"] = f"{mem_limit}Mi"
            self.api_client_appsv1.patch_namespaced_deployment(
                name=deployment_name, namespace=self.namespace, body=deployment)
            print(
                f"[K8sManager Limit] Set {deployment_name} limit cpu from {old_cpu_limit} to {cpu_limit}m.")
            print(
                f"[K8sManager Limit] Set {deployment_name} limit memory from {old_memory_limit} to {mem_limit}Mi.")
        else:
            deployment.spec.template.spec.containers[0].resources.limits = {"cpu": f"{cpu_limit}m", "memory": f"{mem_limit}Mi"}
            self.api_client_appsv1.patch_namespaced_deployment(
                name=deployment_name, namespace=self.namespace, body=deployment)
            print(
                f"[K8sManager Limit] Set {deployment_name} limit cpu from Unlimited to {cpu_limit}m.")
            print(
                f"[K8sManager Limit] Set {deployment_name} limit memory from Unlimited to {mem_limit}Mi.")
        sleep(2)

    def set_restart(self, deployment_name):
        deployment = self.api_client_appsv1.read_namespaced_deployment(
            deployment_name, self.namespace)
        deployment.spec.template.spec.restart_policy = "Always"
        self.api_client_appsv1.patch_namespaced_deployment(
                name=deployment_name, namespace=self.namespace, body=deployment)
        print(
                f"[K8sManager Restart] Set {deployment_name} restart policy to True.")
        sleep(2)