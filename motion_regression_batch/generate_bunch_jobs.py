#!/usr/bin/env python3
"""
Kubernetes Job Generator Script

This script generates multiple Kubernetes jobs from a template YAML file
by substituting variables in the format $(var_name) with different values
and submits them using kubectl.
"""

import os
import sys
import yaml
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Any
import argparse


class KubernetesJobGenerator:
    def __init__(self, template_file: str, output_dir: str = "batch_job"):
        """
        Initialize the job generator.
        
        Args:
            template_file: Path to the template YAML file
            output_dir: Directory to store generated job files
        """
        self.template_file = template_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
    def load_template(self) -> str:
        """Load the template YAML file content."""
        try:
            with open(self.template_file, 'r') as f:
                return f.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file '{self.template_file}' not found")
        except Exception as e:
            raise Exception(f"Error reading template file: {e}")
    
    def substitute_variables(self, template_content: str, variables: Dict[str, Any]) -> str:
        """
        Substitute variables in the template content.
        
        Args:
            template_content: The template content as string
            variables: Dictionary of variable names and their values
            
        Returns:
            Content with variables substituted
        """
        result = template_content
        
        for var_name, var_value in variables.items():
            placeholder = f"$({var_name})"
            result = result.replace(placeholder, str(var_value))
            
        return result
    
    def generate_job_file(self, variables: Dict[str, Any], job_name: str = None) -> str:
        """
        Generate a job YAML file from template with given variables.
        
        Args:
            variables: Dictionary of variable names and their values
            job_name: Optional custom job name
            
        Returns:
            Path to the generated job file
        """
        template_content = self.load_template()
        substituted_content = self.substitute_variables(template_content, variables)
        
        # Generate filename based on variables or use provided job_name
        if job_name is None:
            # Create a filename based on variable values
            var_str = "_".join([f"{k}_{v}" for k, v in sorted(variables.items())])
            filename = f"job_{var_str}.yaml"
        else:
            filename = f"{job_name}.yaml"
        
        job_file_path = self.output_dir / filename
        
        with open(job_file_path, 'w') as f:
            f.write(substituted_content)
            
        return str(job_file_path)
    
    def submit_job(self, job_file_path: str) -> bool:
        """
        Submit a job to Kubernetes using kubectl.
        
        Args:
            job_file_path: Path to the job YAML file
            
        Returns:
            True if successful, False otherwise
        """
        try:
            result = subprocess.run(
                ['kubectl', 'create', '-f', job_file_path],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"v Successfully submitted job: {job_file_path}")
            print(f"Output: {result.stdout.strip()}")
            return True
        except subprocess.CalledProcessError as e:
            print(f"x Failed to submit job: {job_file_path}")
            print(f"Error: {e.stderr.strip()}")
            return False
        except FileNotFoundError:
            print("x kubectl not found. Please ensure kubectl is installed and in PATH")
            return False
    
    def generate_and_submit_batch(self, variable_combinations: List[Dict[str, Any]], 
                                 submit_jobs: bool = True, 
                                 cleanup: bool = False) -> List[str]:
        """
        Generate and optionally submit multiple jobs.
        
        Args:
            variable_combinations: List of variable dictionaries
            submit_jobs: Whether to submit jobs to Kubernetes
            cleanup: Whether to clean up generated files after submission
            
        Returns:
            List of generated job file paths
        """
        generated_files = []
        successful_submissions = 0
        
        print(f"Generating {len(variable_combinations)} jobs...")
        
        for i, variables in enumerate(variable_combinations, 1):
            print(f"\n--- Job {i}/{len(variable_combinations)} ---")
            print(f"Variables: {variables}")
            
            try:
                job_file_path = self.generate_job_file(variables)
                generated_files.append(job_file_path)
                print(f"Generated: {job_file_path}")
                
                if submit_jobs:
                    if self.submit_job(job_file_path):
                        successful_submissions += 1
                        
                        if cleanup:
                            os.remove(job_file_path)
                            print(f"Cleaned up: {job_file_path}")
                            
            except Exception as e:
                print(f"x Error generating job {i}: {e}")
        
        print(f"\n=== Summary ===")
        print(f"Total jobs generated: {len(generated_files)}")
        if submit_jobs:
            print(f"Successfully submitted: {successful_submissions}")
            print(f"Failed submissions: {len(generated_files) - successful_submissions}")
        
        return generated_files


def create_variable_combinations(variable_options: Dict[str, List[Any]]) -> List[Dict[str, Any]]:
    """
    Create all possible combinations of variables from the given options.
    
    Args:
        variable_options: Dictionary where keys are variable names and values are lists of possible values
        
    Returns:
        List of dictionaries, each representing one combination of variables
    """
    import itertools
    
    # Get all variable names and their possible values
    var_names = list(variable_options.keys())
    var_values = list(variable_options.values())
    
    # Generate all combinations
    combinations = []
    for combination in itertools.product(*var_values):
        var_dict = dict(zip(var_names, combination))
        combinations.append(var_dict)
    
    return combinations


def main():
    parser = argparse.ArgumentParser(description='Generate and submit Kubernetes jobs from template')
    parser.add_argument('template_file', help='Path to the template YAML file')
    parser.add_argument('variable_file', help='Variable options yml file')
    parser.add_argument('--output-dir', default='batch_job', help='Output directory for generated jobs')
    parser.add_argument('--no-submit', action='store_true', help='Generate files without submitting to Kubernetes')
    parser.add_argument('--cleanup', action='store_true', help='Clean up generated files after submission')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be generated without creating files')
    
    args = parser.parse_args()
    
    # Load variable options
    try:
        with open(args.variable_file, 'r') as f:
            variable_options = yaml.safe_load(f)
    except Exception as e:
        print(f"x Error loading variables file: {e}")
        sys.exit(1)
    
    # Create variable combinations
    combinations = create_variable_combinations(variable_options)
    
    if args.dry_run:
        print("=== DRY RUN MODE ===")
        print(f"Template file: {args.template_file}")
        print(f"Variable options: {variable_options}")
        print(f"Total combinations: {len(combinations)}")
        print("\nCombinations that would be generated:")
        for i, combo in enumerate(combinations, 1):
            print(f"  {i}. {combo}")
        return
    
    # Initialize generator
    generator = KubernetesJobGenerator(args.template_file, args.output_dir)
    
    # Generate and submit jobs
    generated_files = generator.generate_and_submit_batch(
        combinations,
        submit_jobs=not args.no_submit,
        cleanup=args.cleanup
    )
    
    if not args.no_submit and not args.cleanup:
        print(f"\nGenerated job files are available in: {args.output_dir}")


if __name__ == "__main__":
    print("here")
    main()
